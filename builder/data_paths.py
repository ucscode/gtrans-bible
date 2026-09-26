"""Canonical filesystem layout for database and generated-data artifacts."""

from __future__ import annotations

from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = REPOSITORY_ROOT / "data"


def database_path(filename: str, data_dir: Path | None = None) -> Path:
    """Return a database artifact path under the dedicated SQLite directory."""

    return Path(data_dir or DEFAULT_DATA_DIR) / "databases" / filename


def generated_path(filename: str, data_dir: Path | None = None) -> Path:
    """Return a generated JSON/CSV/report path under the reports directory."""

    return Path(data_dir or DEFAULT_DATA_DIR) / "generated" / filename


DATABASE_FILENAMES = (
    "bible.sqlite",
    "igbob.sqlite",
    "igbob-modern.sqlite",
    "kjv.sqlite",
    "oicb.sqlite",
    "oicb-google-en.sqlite",
    "igbob-mobobi-candidate.sqlite",
)


def database_paths(data_dir: Path | None = None) -> dict[str, Path]:
    """Return the canonical paths for all known database artifacts."""

    return {name.removesuffix(".sqlite"): database_path(name, data_dir) for name in DATABASE_FILENAMES}
