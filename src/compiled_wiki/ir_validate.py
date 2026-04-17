from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def _load_schema(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _validate_array_file(
    *,
    repo_root: Path,
    rel_path: str,
    schema_path: Path,
    label: str,
) -> list[str]:
    errors: list[str] = []
    data_path = repo_root / rel_path
    if not data_path.is_file():
        errors.append(f"missing file: {rel_path}")
        return errors
    try:
        with data_path.open(encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"{rel_path}: invalid JSON ({e})"]
    if not isinstance(data, list):
        return [f"{rel_path}: root must be a JSON array"]

    schema = _load_schema(schema_path)
    validator = Draft202012Validator(schema)
    for i, item in enumerate(data):
        for err in validator.iter_errors(item):
            loc = ".".join(str(p) for p in err.absolute_path) or "(root)"
            errors.append(f"{rel_path}[{i}] {label}: {loc}: {err.message}")
    return errors


def validate_ir(repo_root: Path) -> list[str]:
    schemas = repo_root / "compiler" / "schemas"
    errs: list[str] = []
    errs += _validate_array_file(
        repo_root=repo_root,
        rel_path="ir/claims.json",
        schema_path=schemas / "claim.schema.json",
        label="claim",
    )
    errs += _validate_array_file(
        repo_root=repo_root,
        rel_path="ir/entities.json",
        schema_path=schemas / "entity.schema.json",
        label="entity",
    )
    errs += _validate_array_file(
        repo_root=repo_root,
        rel_path="ir/conflicts.json",
        schema_path=schemas / "conflict.schema.json",
        label="conflict",
    )
    return errs
