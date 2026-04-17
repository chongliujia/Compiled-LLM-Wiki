# `ir/` — Intermediate representation

Structured **claims**, **entities**, and **conflicts**. This layer is the ground truth for factual compilation; `wiki/` is a derived view.

## Files

| File | Purpose |
|------|---------|
| `entities.json` | Canonical entities, aliases, claim ids |
| `claims.json` | All claims with `source_id` and metadata |
| `conflicts.json` | Explicit contradictions between claims |
| `index.json` | Built retrieval index for `cw ask`/`cw chat` (generated via `cw index build`) |

Schemas live in `compiler/schemas/`.
