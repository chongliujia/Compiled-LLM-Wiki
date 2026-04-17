# Entity pages

One page per canonical entity, aligned with `ir/entities.json`.

Each page should:

- Summarize only what claims in `ir/claims.json` support (no invented facts).
- Link or list claim ids used in the summary.
- Include a **Conflicts** section when `ir/conflicts.json` references this entity.

Agents: patch sections incrementally; do not regenerate whole pages unless rebuilding from scratch is explicitly requested.
