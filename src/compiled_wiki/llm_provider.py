from __future__ import annotations

import os
from pathlib import Path


DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"


def load_dotenv(repo_root: Path) -> dict[str, str]:
    env_path = repo_root / ".env"
    if not env_path.is_file():
        return {}
    out: dict[str, str] = {}
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            out[key] = value
    return out


def get_llm_config(repo_root: Path, provider: str, model: str | None) -> tuple[str, str, str]:
    dotenv = load_dotenv(repo_root)
    if provider != "deepseek":
        raise ValueError(f"Unsupported provider: {provider}")
    api_key = os.environ.get("DEEPSEEK_API_KEY") or dotenv.get("DEEPSEEK_API_KEY") or ""
    base_url = os.environ.get("DEEPSEEK_BASE_URL") or dotenv.get("DEEPSEEK_BASE_URL") or DEFAULT_DEEPSEEK_BASE_URL
    selected_model = model or os.environ.get("DEEPSEEK_MODEL") or dotenv.get("DEEPSEEK_MODEL") or DEFAULT_DEEPSEEK_MODEL
    if not api_key:
        raise ValueError("Missing DEEPSEEK_API_KEY. Add it to .env or export it in the shell.")
    return api_key, base_url, selected_model


def is_provider_configured(repo_root: Path, provider: str) -> bool:
    if provider != "deepseek":
        return False
    dotenv = load_dotenv(repo_root)
    api_key = os.environ.get("DEEPSEEK_API_KEY") or dotenv.get("DEEPSEEK_API_KEY") or ""
    return bool(api_key.strip())
