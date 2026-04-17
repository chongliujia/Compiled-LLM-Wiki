from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _load_json_array(path: Path) -> list[dict] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, list):
        return None
    out: list[dict] = []
    for x in data:
        if isinstance(x, dict):
            out.append(x)
    return out


def lint_repo(repo_root: Path) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) per AGENTS.md-style checks (subset)."""
    errors: list[str] = []
    warnings: list[str] = []

    claims_path = repo_root / "ir" / "claims.json"
    entities_path = repo_root / "ir" / "entities.json"
    conflicts_path = repo_root / "ir" / "conflicts.json"

    claims = _load_json_array(claims_path)
    entities = _load_json_array(entities_path)
    conflicts = _load_json_array(conflicts_path)

    if claims is None:
        errors.append("ir/claims.json missing or not a JSON array of objects")
        claim_by_id: dict[str, dict] = {}
    else:
        ids = [c.get("id") for c in claims]
        for cid, n in Counter(ids).items():
            if cid is None:
                errors.append("claim with null id")
            elif n > 1:
                errors.append(f"duplicate claim id: {cid!r} ({n} times)")
        claim_by_id = {str(c["id"]): c for c in claims if c.get("id") is not None}
        for i, c in enumerate(claims):
            sid = c.get("source_id")
            if not sid or (isinstance(sid, str) and not sid.strip()):
                errors.append(f"ir/claims.json[{i}] claim id={c.get('id')!r}: empty source_id")
            elif isinstance(sid, str):
                raw_dir = repo_root / "raw" / sid
                if not raw_dir.is_dir():
                    warnings.append(
                        f"claim id={c.get('id')!r}: source_id {sid!r} has no folder raw/{sid}/ "
                        "(add sources there, or fix source_id)"
                    )

    if entities is None:
        errors.append("ir/entities.json missing or not a JSON array of objects")
    else:
        eids = [e.get("id") for e in entities]
        for eid, n in Counter(eids).items():
            if eid is None:
                errors.append("entity with null id")
            elif n > 1:
                errors.append(f"duplicate entity id: {eid!r} ({n} times)")
        names = [e.get("canonical_name") for e in entities if e.get("canonical_name")]
        for name, n in Counter(names).items():
            if n > 1:
                warnings.append(f"duplicate canonical_name (possible merge candidate): {name!r}")

        for i, e in enumerate(entities):
            for cid in e.get("claim_ids") or []:
                if cid not in claim_by_id:
                    errors.append(
                        f"ir/entities.json[{i}] entity id={e.get('id')!r}: "
                        f"unknown claim_id {cid!r}"
                    )

    if conflicts is None:
        errors.append("ir/conflicts.json missing or not a JSON array of objects")
    else:
        for i, row in enumerate(conflicts):
            cids = row.get("claim_ids") or []
            if len(cids) < 2:
                errors.append(f"ir/conflicts.json[{i}]: conflict needs at least 2 claim_ids")
            for cid in cids:
                if cid not in claim_by_id:
                    errors.append(
                        f"ir/conflicts.json[{i}] id={row.get('id')!r}: unknown claim_id {cid!r}"
                    )

    wiki_root = repo_root / "wiki"
    if wiki_root.is_dir():
        for md in sorted(wiki_root.rglob("*.md")):
            text = md.read_text(encoding="utf-8", errors="replace")
            for m in _LINK_RE.finditer(text):
                target = m.group(1).strip()
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                if target.startswith("#"):
                    continue
                rel = (md.parent / target).resolve()
                try:
                    rel.relative_to(repo_root.resolve())
                except ValueError:
                    warnings.append(f"link escapes repo? {md.relative_to(repo_root)} -> {target!r}")
                    continue
                if not rel.exists():
                    errors.append(
                        f"broken link in {md.relative_to(repo_root)} -> {target!r} "
                        f"(resolved {rel.relative_to(repo_root)})"
                    )

    return errors, warnings
