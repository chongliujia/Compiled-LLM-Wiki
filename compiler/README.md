# `compiler/` — Schemas and tooling (optional)

JSON Schemas for validating `ir/*.json` live in `schemas/`.

Future: lint passes, codegen, or CI checks can live here. They must not modify `raw/`.

Installed from repo root with `pip install -e .`, the **`cw`** command runs lightweight checks (see root [`README.md`](../README.md)).
