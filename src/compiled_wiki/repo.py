from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    """Walk upward from cwd (or start) until AGENTS.md and ir/claims.json exist."""
    cur = (start or Path.cwd()).resolve()
    for p in [cur, *cur.parents]:
        if (p / "AGENTS.md").is_file() and (p / "ir" / "claims.json").is_file():
            return p
    raise FileNotFoundError(
        "Could not find Compiled-Wiki repo root (need AGENTS.md and ir/claims.json). "
        "Run this command from inside the repository."
    )
