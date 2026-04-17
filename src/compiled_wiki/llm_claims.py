from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from compiled_wiki.llm_provider import get_llm_config


@dataclass(frozen=True)
class LlmClaimsResult:
    source_id: str
    output_path: Path
    provider: str
    model: str
    claim_count: int


def _read_extract(repo_root: Path, source_id: str, max_chars: int) -> str:
    path = repo_root / "ir" / "extracts" / f"{source_id}.md"
    if not path.is_file():
        raise FileNotFoundError(f"Missing Markdown extract: ir/extracts/{source_id}.md")
    text = path.read_text(encoding="utf-8")
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n[TRUNCATED FOR LLM CANDIDATE EXTRACTION]\n"
    return text


def _candidate_schema_example(source_id: str) -> str:
    return json.dumps(
        {
            "source_id": source_id,
            "claims": [
                {
                    "subject": "paper or method name",
                    "predicate": "proposes",
                    "object": "specific sourced statement",
                    "claim_type": "SourceFact",
                    "evidence_span": "short exact supporting span from the extract",
                    "status": "supported",
                    "notes": "why this is a reusable claim",
                }
            ],
        },
        indent=2,
        ensure_ascii=False,
    )


def _normalize_candidate_payload(payload: Any, source_id: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("LLM response root must be a JSON object")
    claims = payload.get("claims")
    if not isinstance(claims, list):
        raise ValueError("LLM response must include a claims array")

    normalized: list[dict[str, Any]] = []
    for row in claims:
        if not isinstance(row, dict):
            continue
        claim = {
            "subject": str(row.get("subject", "")).strip(),
            "predicate": str(row.get("predicate", "")).strip(),
            "object": str(row.get("object", "")).strip(),
            "claim_type": str(row.get("claim_type", "SourceFact")).strip() or "SourceFact",
            "source_id": source_id,
            "evidence_span": row.get("evidence_span") if row.get("evidence_span") is not None else None,
            "status": str(row.get("status", "supported")).strip() or "supported",
            "notes": row.get("notes") if row.get("notes") is not None else None,
        }
        if claim["subject"] and claim["predicate"] and claim["object"]:
            normalized.append(claim)
    return {"source_id": source_id, "claims": normalized}


def generate_llm_claim_candidates(
    *,
    repo_root: Path,
    source_id: str,
    provider: str = "deepseek",
    model: str | None = None,
    max_chars: int = 22000,
    overwrite: bool = False,
) -> LlmClaimsResult:
    api_key, base_url, selected_model = get_llm_config(repo_root, provider, model)
    extract = _read_extract(repo_root, source_id, max_chars)
    output_dir = repo_root / "ir" / "candidates"
    output_path = output_dir / f"{source_id}.deepseek.claims.json"
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Candidate file already exists: {output_path.relative_to(repo_root)}")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("OpenAI Python SDK is required for DeepSeek-compatible calls.") from exc

    system_prompt = (
        "You are a Knowledge Compiler Agent. Extract reusable claims from academic paper text. "
        "Return JSON only. Do not invent facts. Every claim must be directly supported by the provided text. "
        "Use claim_type SourceFact only for direct statements. If attribution is unclear, use status unknown. "
        "Keep evidence_span short and copied from the provided extract."
    )
    user_prompt = (
        "Extract 6 to 10 high-value JSON candidate claims for compiled-wiki ingest.\n\n"
        "Required JSON shape example:\n"
        f"{_candidate_schema_example(source_id)}\n\n"
        "Source extract:\n"
        f"{extract}"
    )

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=selected_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=3000,
        stream=False,
    )
    content = response.choices[0].message.content or ""
    parsed = json.loads(content)
    normalized = _normalize_candidate_payload(parsed, source_id)
    artifact = {
        "source_id": source_id,
        "provider": provider,
        "model": selected_model,
        "base_url": base_url,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "candidate_not_ingested",
        "claims": normalized["claims"],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return LlmClaimsResult(
        source_id=source_id,
        output_path=output_path,
        provider=provider,
        model=selected_model,
        claim_count=len(normalized["claims"]),
    )
