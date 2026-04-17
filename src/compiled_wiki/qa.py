from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from compiled_wiki.llm_provider import get_llm_config, is_provider_configured

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*|[\u4e00-\u9fff]")
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "based",
    "be",
    "by",
    "do",
    "does",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "paper",
    "that",
    "the",
    "this",
    "to",
    "use",
    "uses",
    "what",
    "with",
}

# Lightweight cross-lingual query expansion for Chinese prompts over mostly English claims.
# This keeps retrieval simple while improving bilingual usability for common technical terms.
_ZH_QUERY_EXPANSIONS: dict[str, str] = {
    "三相逆变器": "three phase inverter",
    "逆变器": "inverter",
    "实验": "experimental",
    "实验误差": "experimental error",
    "误差": "error",
    "最大误差": "maximum error",
    "最大": "maximum",
    "参数": "parameter",
    "估计": "estimate estimated",
    "硬件": "hardware",
    "额外硬件": "extra hardware",
    "电压预测": "voltage prediction",
    "物理嵌入": "physics embedded",
    "物理信息": "physics information",
    "电容": "capacitance",
    "电感": "inductance",
}


@dataclass(frozen=True)
class SearchHit:
    score: float
    claim: dict[str, Any]
    entity: dict[str, Any] | None
    wiki_path: str | None


def _load_json_array(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [x for x in data if isinstance(x, dict)] if isinstance(data, list) else []


def _load_index(repo_root: Path) -> dict[str, Any] | None:
    path = repo_root / "ir" / "index.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    if not isinstance(data.get("docs"), list) or not isinstance(data.get("token_df"), dict):
        return None
    return data


def _tokens(text: str) -> list[str]:
    out: list[str] = []
    for raw in _TOKEN_RE.findall(text):
        t = raw.lower()
        # Single Han characters are too noisy for lexical retrieval over English claims.
        if len(t) == 1 and "\u4e00" <= t <= "\u9fff":
            continue
        if t in _STOPWORDS:
            continue
        out.append(t)
    return out


def _expand_query_text(query: str) -> str:
    if not any("\u4e00" <= ch <= "\u9fff" for ch in query):
        return query
    hints: list[str] = []
    for zh, en in _ZH_QUERY_EXPANSIONS.items():
        if zh in query:
            hints.append(en)
    if not hints:
        return query
    return f"{query} {' '.join(hints)}"


def _claim_text(claim: dict[str, Any], entity: dict[str, Any] | None) -> str:
    parts = [
        claim.get("subject", ""),
        claim.get("predicate", ""),
        claim.get("object", ""),
        claim.get("evidence_span", ""),
        claim.get("source_id", ""),
    ]
    if entity:
        parts.append(entity.get("canonical_name", ""))
        parts.extend(entity.get("aliases") or [])
    return " ".join(str(p) for p in parts if p)


def _rewrite_query_with_llm(
    repo_root: Path,
    query: str,
    provider: str,
    model: str | None,
) -> str | None:
    if not any("\u4e00" <= ch <= "\u9fff" for ch in query):
        return None
    try:
        from openai import OpenAI
    except ImportError:
        return None
    try:
        api_key, base_url, selected_model = get_llm_config(repo_root, provider, model)
    except ValueError:
        return None
    system_prompt = (
        "You rewrite user questions into concise English retrieval queries for technical papers. "
        "Return one short line only. No quotes, no extra explanation."
    )
    user_prompt = (
        "Rewrite this question into an English retrieval query with key technical terms, "
        "component names, metrics, and intent.\n"
        f"Question: {query}"
    )
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=selected_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        max_tokens=80,
        stream=False,
    )
    rewritten = (response.choices[0].message.content or "").strip()
    return rewritten or None


def search_claims(
    repo_root: Path,
    query: str,
    limit: int = 5,
    query_rewrite_provider: str | None = None,
    query_rewrite_model: str | None = None,
) -> list[SearchHit]:
    claims = _load_json_array(repo_root / "ir" / "claims.json")
    entities = _load_json_array(repo_root / "ir" / "entities.json")
    claim_by_id = {str(c.get("id")): c for c in claims if c.get("id")}
    entity_by_id = {str(e.get("id")): e for e in entities if e.get("id")}
    entity_by_claim: dict[str, dict[str, Any]] = {}
    for entity in entities:
        for cid in entity.get("claim_ids") or []:
            entity_by_claim[str(cid)] = entity

    query_variants: list[tuple[str, float]] = [(_expand_query_text(query), 1.15)]
    if query_rewrite_provider:
        try:
            rewritten = _rewrite_query_with_llm(repo_root, query, query_rewrite_provider, query_rewrite_model)
        except Exception:
            rewritten = None
        if rewritten and all(rewritten != q for q, _ in query_variants):
            query_variants.append((rewritten, 1.0))

    query_count_list: list[tuple[dict[str, int], float]] = []
    for q, weight in query_variants:
        q_tokens = _tokens(q)
        if not q_tokens:
            continue
        query_count_list.append(({t: q_tokens.count(t) for t in set(q_tokens)}, weight))
    if not query_count_list:
        return []

    index = _load_index(repo_root)
    docs_data: list[tuple[dict[str, Any], dict[str, Any] | None, str | None, dict[str, int]]] = []
    token_df: dict[str, int] = {}
    if index is not None:
        raw_token_df = index.get("token_df") or {}
        token_df = {str(k): int(v) for k, v in raw_token_df.items() if isinstance(v, (int, float))}
        for row in index.get("docs") or []:
            if not isinstance(row, dict):
                continue
            claim_id = str(row.get("claim_id") or "")
            claim = claim_by_id.get(claim_id)
            if not claim:
                continue
            entity = entity_by_claim.get(claim_id)
            if not entity:
                entity_id = row.get("entity_id")
                entity = entity_by_id.get(str(entity_id)) if entity_id else None
            wiki_path = row.get("wiki_path") or (entity.get("wiki_path") if entity else None)
            raw_freq = row.get("token_freq") or {}
            if not isinstance(raw_freq, dict):
                continue
            freq = {str(k): int(v) for k, v in raw_freq.items() if isinstance(v, (int, float)) and int(v) > 0}
            if not freq:
                continue
            docs_data.append((claim, entity, wiki_path, freq))
    else:
        doc_token_df: Counter[str] = Counter()
        for claim in claims:
            cid = str(claim.get("id", ""))
            entity = entity_by_claim.get(cid)
            if not entity:
                entity_ids = claim.get("entity_ids") or []
                entity = entity_by_id.get(str(entity_ids[0])) if entity_ids else None
            freq_counter: Counter[str] = Counter(_tokens(_claim_text(claim, entity)))
            if not freq_counter:
                continue
            doc_token_df.update(freq_counter.keys())
            wiki_path = entity.get("wiki_path") if entity else None
            docs_data.append((claim, entity, wiki_path, dict(freq_counter)))
        token_df = dict(doc_token_df)

    if not docs_data:
        return []
    doc_count = len(docs_data)

    hits: list[SearchHit] = []
    for claim, entity, wiki_path, doc_counts in docs_data:
        d_vec_sq = 0.0
        for t, tf in doc_counts.items():
            df = max(1, int(token_df.get(t, 1)))
            idf = math.log((doc_count + 1) / (df + 1)) + 1.0
            d_vec_sq += (tf * idf) * (tf * idf)
        d_norm = math.sqrt(d_vec_sq)
        if d_norm <= 0.0:
            continue
        best_score = 0.0
        matched_variants = 0
        for query_counts, weight in query_count_list:
            overlap = set(query_counts) & set(doc_counts)
            if not overlap:
                continue
            matched_variants += 1
            dot = 0.0
            q_vec_sq = 0.0
            for t, q_tf in query_counts.items():
                df = max(1, int(token_df.get(t, 1)))
                idf = math.log((doc_count + 1) / (df + 1)) + 1.0
                q_weight = q_tf * idf
                q_vec_sq += q_weight * q_weight
                if t in doc_counts:
                    dot += q_weight * (doc_counts[t] * idf)
            q_norm = math.sqrt(q_vec_sq)
            cosine = dot / (q_norm * d_norm) if q_norm and d_norm else 0.0
            query_mass = sum(query_counts.values())
            overlap_mass = sum(min(query_counts[t], doc_counts[t]) for t in overlap)
            coverage = (overlap_mass / query_mass) if query_mass else 0.0
            score = weight * (cosine + 0.15 * coverage)
            if score > best_score:
                best_score = score
        if best_score <= 0.0:
            continue
        score = best_score + 0.01 * max(matched_variants - 1, 0)
        if str(claim.get("status")) == "supported":
            score += 0.03
        hits.append(SearchHit(score=score, claim=claim, entity=entity, wiki_path=wiki_path))

    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[:limit]


def format_references(repo_root: Path, hits: list[SearchHit]) -> str:
    if not hits:
        return "No matching claims found in IR."
    lines = ["Retrieved references:"]
    for i, hit in enumerate(hits, start=1):
        claim = hit.claim
        source_id = claim.get("source_id", "")
        raw_dir = f"raw/{source_id}/" if source_id else "(missing source_id)"
        wiki = f"wiki/{hit.wiki_path}" if hit.wiki_path else "(no wiki page)"
        lines.append(
            f"[{i}] {claim.get('id')} | score={hit.score:.3f} | status={claim.get('status')} | "
            f"source={source_id}"
        )
        lines.append(f"    claim: {claim.get('subject')} -- {claim.get('predicate')} -- {claim.get('object')}")
        if claim.get("evidence_span"):
            lines.append(f"    evidence: {claim.get('evidence_span')}")
        lines.append(f"    raw: {raw_dir}")
        lines.append(f"    wiki: {wiki}")
    return "\n".join(lines)


def answer_from_hits(query: str, hits: list[SearchHit]) -> str:
    if not hits:
        return "Answer: I could not find supported claims in the current wiki/IR for this question."
    zh = any("\u4e00" <= ch <= "\u9fff" for ch in query)
    lines = [f"Answer: {'根据' if zh else 'Based on'} {len(hits)} {'条检索到的 claim' if zh else 'retrieved claim(s)'}:"]
    for i, hit in enumerate(hits, start=1):
        c = hit.claim
        subject = c.get("subject")
        predicate = str(c.get("predicate", "")).replace("_", " ")
        obj = c.get("object")
        if zh:
            lines.append(f"- [{i}] `{subject}` 的记录显示：{predicate} -> {obj}。")
        else:
            lines.append(f"- [{i}] `{subject}` {predicate}: {obj}.")
    if zh:
        lines.append("上面的 Retrieved references 是引用链；wiki 页面是视图，IR claims 是事实层。")
    else:
        lines.append("Use the retrieved references above as the citation trail; wiki pages are views, IR claims are the ground-truth layer.")
    return "\n".join(lines)


def _hits_context(hits: list[SearchHit]) -> str:
    lines: list[str] = []
    for i, hit in enumerate(hits, start=1):
        claim = hit.claim
        lines.append(f"[{i}] id={claim.get('id')} source_id={claim.get('source_id')} status={claim.get('status')}")
        lines.append(f"subject={claim.get('subject')}")
        lines.append(f"predicate={claim.get('predicate')}")
        lines.append(f"object={claim.get('object')}")
        lines.append(f"evidence={claim.get('evidence_span')}")
        if hit.wiki_path:
            lines.append(f"wiki=wiki/{hit.wiki_path}")
        lines.append("")
    return "\n".join(lines).strip()


def answer_from_hits_llm(
    repo_root: Path,
    query: str,
    hits: list[SearchHit],
    provider: str,
    model: str | None,
) -> str:
    if not hits:
        return "Answer: I could not find supported claims in the current wiki/IR for this question."
    api_key, base_url, selected_model = get_llm_config(repo_root, provider, model)
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("OpenAI Python SDK is required for DeepSeek-compatible calls.") from exc
    context = _hits_context(hits)
    system_prompt = (
        "You answer questions for a compiled wiki. Use only the retrieved references provided by the user. "
        "Do not add external facts. If evidence is insufficient, say so. Keep the answer concise."
    )
    user_prompt = (
        f"Question:\n{query}\n\n"
        "Retrieved references:\n"
        f"{context}\n\n"
        "Write a direct answer grounded only in these references. "
        "At the end, include a short citation list like [c_id_1, c_id_2]."
    )
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=selected_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        max_tokens=700,
        stream=False,
    )
    content = (response.choices[0].message.content or "").strip()
    if not content:
        return "Answer: LLM returned an empty response."
    return f"Answer (LLM, {provider}/{selected_model}):\n{content}"


def resolve_answer_provider(repo_root: Path, provider: str) -> str:
    if provider == "auto":
        return "deepseek" if is_provider_configured(repo_root, "deepseek") else "local"
    return provider


def run_ask(
    repo_root: Path,
    question: str,
    limit: int = 5,
    show_refs: bool = True,
    provider: str = "auto",
    model: str | None = None,
) -> str:
    # Query workflow: wiki/index.md is read first, then IR claims are used for citations.
    index = repo_root / "wiki" / "index.md"
    if not index.is_file():
        raise FileNotFoundError("Missing wiki/index.md")
    _ = index.read_text(encoding="utf-8")
    resolved_provider = resolve_answer_provider(repo_root, provider)
    rewrite_provider = resolved_provider if resolved_provider != "local" else None
    hits = search_claims(
        repo_root,
        question,
        limit=limit,
        query_rewrite_provider=rewrite_provider,
        query_rewrite_model=model,
    )
    parts: list[str] = []
    if show_refs:
        parts.append(format_references(repo_root, hits))
        parts.append("")
    if resolved_provider == "local":
        parts.append(answer_from_hits(question, hits))
    else:
        try:
            parts.append(answer_from_hits_llm(repo_root, question, hits, resolved_provider, model))
        except Exception as e:
            raise RuntimeError(f"LLM call failed ({type(e).__name__}): {e}") from e
    return "\n".join(parts)
