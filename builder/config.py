"""Repository-local configuration loading without exposing secret values."""

from __future__ import annotations

import os
from pathlib import Path


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _fallback_load_dotenv(env_path: Path) -> None:
    """Small fallback for source checkouts before optional dependencies install."""

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def load_repository_env(root: Path | None = None) -> Path | None:
    """Load ``root/.env`` without overriding existing process variables.

    Relative ``GOOGLE_APPLICATION_CREDENTIALS`` paths are resolved against the
    repository root, making them independent of the caller's working directory.
    """

    root = (root or repository_root()).resolve()
    env_path = root / ".env"
    if env_path.exists():
        try:
            from dotenv import load_dotenv
        except ImportError:
            _fallback_load_dotenv(env_path)
        else:
            load_dotenv(dotenv_path=env_path, override=False)

    credential_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if credential_path:
        candidate = Path(credential_path)
        if not candidate.is_absolute():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(root / candidate)
    return env_path if env_path.exists() else None


def resolve_project_id(cli_project_id: str | None = None) -> str | None:
    """Apply CLI > process environment/.env > default precedence."""

    return cli_project_id or os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCLOUD_PROJECT")
