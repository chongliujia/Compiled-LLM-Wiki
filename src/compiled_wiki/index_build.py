from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*|[\u4e00-\u9fff]")
STOPWORDS = {
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

# Domain aliases used by the index to improve retrieval coverage.
PREDICATE_ALIASES: dict[str, list[str]] = {
    "proposes": ["method", "approach", "model"],
    "estimates": ["estimation", "parameter estimation"],
    "does_not_require": ["no additional hardware", "hardware free"],
    "shows_maximum_error": ["maximum error", "max error", "experimental error"],
    "is_validated_with": ["validated", "verification", "experiment", "simulation"],
    "embeds": ["physics embedded", "physical relation"],
    "is_enhanced_with": ["enhanced", "additional layers"],
}


@dataclass(frozen=True)
class BuildIndexResult:
    output_path: Path
    doc_count: int
    token_count: int


def _load_json_array(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []
    return [x for x in data if isinstance(x, dict)]


def _tokens(text: str) -> list[str]:
    out: list[str] = []
    for raw in TOKEN_RE.findall(text):
        t = raw.lower()
        if len(t) == 1 and "\u4e00" <= t <= "\u9fff":
            continue
        if t in STOPWORDS:
            continue
        out.append(t)
    return out


def _add_terms(counter: Counter[str], text: str, weight: int = 1) -> None:
    for t in _tokens(text):
        counter[t] += weight


def build_ir_index(repo_root: Path, overwrite: bool = False) -> BuildIndexResult:
    claims = _load_json_array(repo_root / "ir" / "claims.json")
    entities = _load_json_array(repo_root / "ir" / "entities.json")
    entity_by_claim: dict[str, dict[str, Any]] = {}
    for entity in entities:
        for cid in entity.get("claim_ids") or []:
            entity_by_claim[str(cid)] = entity

    docs: list[dict[str, Any]] = []
    token_df: Counter[str] = Counter()

    for claim in claims:
        claim_id = str(claim.get("id") or "")
        if not claim_id:
            continue
        entity = entity_by_claim.get(claim_id)
        freq: Counter[str] = Counter()
        _add_terms(freq, str(claim.get("subject", "")), weight=3)
        _add_terms(freq, str(claim.get("predicate", "")), weight=2)
        _add_terms(freq, str(claim.get("object", "")), weight=3)
        _add_terms(freq, str(claim.get("evidence_span", "")), weight=1)
        _add_terms(freq, str(claim.get("source_id", "")), weight=1)
        if entity:
            _add_terms(freq, str(entity.get("canonical_name", "")), weight=2)
            for alias in entity.get("aliases") or []:
                _add_terms(freq, str(alias), weight=2)
            wiki_path = entity.get("wiki_path")
            entity_id = entity.get("id")
        else:
            wiki_path = None
            entity_id = None

        predicate = str(claim.get("predicate", ""))
        for alias_text in PREDICATE_ALIASES.get(predicate, []):
            _add_terms(freq, alias_text, weight=2)

        if not freq:
            continue
        token_df.update(freq.keys())
        docs.append(
            {
                "claim_id": claim_id,
                "source_id": claim.get("source_id"),
                "status": claim.get("status"),
                "entity_id": entity_id,
                "wiki_path": wiki_path,
                "token_freq": dict(freq),
            }
        )

    index = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "doc_count": len(docs),
        "token_count": len(token_df),
        "docs": docs,
        "token_df": dict(token_df),
        "predicate_aliases": PREDICATE_ALIASES,
    }

    output_path = repo_root / "ir" / "index.json"
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Index already exists: {output_path.relative_to(repo_root)}")
    output_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return BuildIndexResult(output_path=output_path, doc_count=len(docs), token_count=len(token_df))
