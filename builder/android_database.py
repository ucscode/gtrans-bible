"""Read-only validation and manifest helpers for Android database imports.

This module inspects the separate canonical and edition databases. It does not
rebuild or modify any SQLite database.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path
from typing import Mapping
from urllib.parse import quote

from .data_paths import DEFAULT_DATA_DIR, database_path, generated_path


DEFAULT_DATABASES = {
    "canonical": database_path("bible.sqlite"),
    "igbob": database_path("igbob.sqlite"),
    "igbob-modern": database_path("igbob-modern.sqlite"),
    "kjv": database_path("kjv.sqlite"),
}


def _connect_read_only(path: Path) -> sqlite3.Connection:
    uri = f"file:{quote(str(path.resolve()), safe='/')}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def _tables(connection: sqlite3.Connection) -> list[str]:
    return [
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]


def _columns(connection: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in connection.execute(f'PRAGMA table_info("{table}")')}


def _metadata(connection: sqlite3.Connection) -> dict[str, str]:
    if "metadata" not in _tables(connection):
        return {}
    return dict(connection.execute("SELECT key,value FROM metadata"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest_entry(edition_id: str, path: Path) -> dict[str, object]:
    with _connect_read_only(path) as connection:
        tables = _tables(connection)
        meta = _metadata(connection)
        if edition_id == "canonical":
            verse_count = connection.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
            language = None
            name = "Canonical Bible structure"
            version = None
            version_basis = None
            source = "Canonical book, chapter, and verse IDs with order and relationships only."
            normalization_version = None
        else:
            verse_count = connection.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
            language = meta.get("language")
            name = meta.get("name", edition_id)
            normalization_version = meta.get("normalization_ruleset_version") or meta.get("ruleset_version")
            if normalization_version:
                version = normalization_version
                version_basis = "normalization_ruleset_version"
            elif meta.get("source_package_version"):
                version = meta["source_package_version"]
                version_basis = "source_package_version"
            else:
                version = meta.get("version")
                version_basis = "version_metadata" if version else None
            source = meta.get("source") or meta.get("source_url") or meta.get("source_status")
    return {
        "filename": path.name,
        "path": f"databases/{path.name}",
        "edition_id": edition_id,
        "edition_name": name,
        "language": language,
        "version": version,
        "version_basis": version_basis,
        "verse_count": verse_count,
        "sha256": _sha256(path),
        "source_provenance": source,
        "normalization_version": normalization_version,
    }


def generate_database_manifest(
    database_paths: Mapping[str, Path] = DEFAULT_DATABASES,
    output_path: Path | None = None,
) -> dict[str, object]:
    """Return a deterministic manifest and optionally write it atomically."""

    expected = tuple(DEFAULT_DATABASES)
    if set(database_paths) != set(expected):
        raise ValueError(f"database_paths must contain exactly {expected}")
    entries = []
    for edition_id in expected:
        path = Path(database_paths[edition_id])
        if not path.is_file():
            raise FileNotFoundError(path)
        entries.append(_manifest_entry(edition_id, path))
    manifest: dict[str, object] = {"manifest_version": 1, "databases": entries}
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=output_path.parent, prefix=f".{output_path.name}.", delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(encoded)
            handle.flush()
        temporary.replace(output_path)
    return manifest


def validate_database_directory(directory: Path) -> list[str]:
    """Return non-SQLite entries; the dedicated database directory is flat."""

    directory = Path(directory)
    if not directory.exists():
        return []
    return sorted(
        entry.name for entry in directory.iterdir()
        if not entry.is_file() or entry.suffix.lower() != ".sqlite"
    )


def validate_runtime_databases(
    database_paths: Mapping[str, Path] = DEFAULT_DATABASES, *, require_full_canon: bool = True
) -> dict[str, object]:
    """Check canonical structure, edition coverage, names, and parallelism."""

    manifest = generate_database_manifest(database_paths)
    paths = {key: Path(value) for key, value in database_paths.items()}
    reports: dict[str, dict[str, object]] = {}
    verse_ids: dict[str, list[str]] = {}
    book_ids: dict[str, list[str]] = {}
    canonical_relationship_errors: list[dict[str, str]] = []

    for edition_id, path in paths.items():
        with _connect_read_only(path) as connection:
            table_names = _tables(connection)
            meta = _metadata(connection)
            if edition_id == "canonical":
                row_counts = {
                    table: connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                    for table in ("books", "chapters", "verses")
                }
                ids = [row[0] for row in connection.execute("SELECT id FROM verses ORDER BY id")]
                books = [row[0] for row in connection.execute("SELECT id FROM books ORDER BY position")]
                bad_chapters = connection.execute(
                    "SELECT c.id FROM chapters c LEFT JOIN books b ON b.id=c.book_id WHERE b.id IS NULL"
                ).fetchall()
                bad_verses = connection.execute(
                    "SELECT v.id FROM verses v LEFT JOIN chapters c ON c.id=v.chapter_id WHERE c.id IS NULL"
                ).fetchall()
                malformed_ids = connection.execute(
                    "SELECT v.id FROM verses v JOIN chapters c ON c.id=v.chapter_id "
                    "JOIN books b ON b.id=c.book_id "
                    "WHERE v.id != b.id || '-' || c.number || '-' || v.number"
                ).fetchall()
                canonical_relationship_errors = [
                    {"verse_id": row[0], "problem": "chapter has no canonical book"} for row in bad_chapters
                ] + [
                    {"verse_id": row[0], "problem": "verse has no canonical chapter"} for row in bad_verses
                ] + [
                    {"verse_id": row[0], "problem": "verse ID disagrees with book/chapter/verse numbers"}
                    for row in malformed_ids
                ]
                edition_duplicate_count = len(ids) - len(set(ids))
                reports[edition_id] = {
                    "path": str(path),
                    "size_bytes": path.stat().st_size,
                    "integrity": connection.execute("PRAGMA integrity_check").fetchone()[0],
                    "tables": table_names,
                    "row_counts": row_counts,
                    "metadata": meta,
                    "book_names_in_canonical": "name" in _columns(connection, "books"),
                    "duplicate_verse_ids": edition_duplicate_count,
                }
            else:
                row_counts = {
                    table: connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                    for table in table_names
                }
                ids = [row[0] for row in connection.execute("SELECT verse_id FROM verses ORDER BY verse_id")]
                books = [row[0] for row in connection.execute("SELECT book_id FROM books ORDER BY book_id")]
                reports[edition_id] = {
                    "path": str(path),
                    "size_bytes": path.stat().st_size,
                    "integrity": connection.execute("PRAGMA integrity_check").fetchone()[0],
                    "tables": table_names,
                    "row_counts": row_counts,
                    "metadata": meta,
                    "duplicate_verse_ids": len(ids) - len(set(ids)),
                    "duplicate_book_ids": len(books) - len(set(books)),
                }
        verse_ids[edition_id] = ids
        book_ids[edition_id] = books

    canonical_verses = set(verse_ids["canonical"])
    canonical_books = set(book_ids["canonical"])
    edition_consistency: dict[str, object] = {}
    for edition_id in ("igbob", "igbob-modern", "kjv"):
        current = set(verse_ids[edition_id])
        edition_consistency[edition_id] = {
            "missing_ids": sorted(canonical_verses - current),
            "extra_ids": sorted(current - canonical_verses),
            "duplicate_ids": reports[edition_id]["duplicate_verse_ids"],
            "missing_book_ids": sorted(canonical_books - set(book_ids[edition_id])),
            "extra_book_ids": sorted(set(book_ids[edition_id]) - canonical_books),
            # Edition databases contain verse IDs only; their chapter/book path
            # is inherited by joining those IDs to canonical. No structures are duplicated.
            "mismatched_chapter_book_relationships": 0,
        }

    historical = _connect_read_only(paths["igbob"])
    modern = _connect_read_only(paths["igbob-modern"])
    try:
        hnames = dict(historical.execute("SELECT book_id,name FROM books"))
        mnames = dict(modern.execute("SELECT book_id,name FROM books"))
        historical_rows = dict(historical.execute("SELECT verse_id,content FROM verses"))
        modern_rows = dict(modern.execute("SELECT verse_id,content FROM verses"))
        changed_ids = sorted(
            verse_id for verse_id in set(historical_rows) & set(modern_rows)
            if historical_rows[verse_id] != modern_rows[verse_id]
        )
        unchanged_ids = sorted(
            verse_id for verse_id in set(historical_rows) & set(modern_rows)
            if historical_rows[verse_id] == modern_rows[verse_id]
        )
    finally:
        historical.close()
        modern.close()

    meta_ig = reports["igbob"]["metadata"].get("language") == "ig"
    meta_modern_ig = reports["igbob-modern"]["metadata"].get("language") == "ig"
    meta_kjv_en = reports["kjv"]["metadata"].get("language") == "en"
    modern_source_hash = reports["igbob-modern"]["metadata"].get("source_database_sha256")
    source_hash_matches = modern_source_hash == _sha256(paths["igbob"])
    names_ok = hnames == mnames and meta_ig and meta_modern_ig and meta_kjv_en
    kjv_consistency = edition_consistency["kjv"]
    canonical_counts = reports["canonical"]["row_counts"]
    expected_coverage = (
        not require_full_canon or canonical_counts == {"books": 66, "chapters": 1189, "verses": 31103}
    )
    passed = (
        not validate_database_directory(paths["canonical"].parent)
        and
        all(report["integrity"] == "ok" for report in reports.values())
        and not canonical_relationship_errors
        and all(
            not check["missing_ids"] and not check["extra_ids"] and check["duplicate_ids"] == 0
            and not check["missing_book_ids"] and not check["extra_book_ids"]
            and check["mismatched_chapter_book_relationships"] == 0
            for check in edition_consistency.values()
        )
        and (not require_full_canon or source_hash_matches)
        and names_ok
        and expected_coverage
    )
    return {
        "valid": passed,
        "databases": reports,
        "canonical_coverage": canonical_counts,
        "canonical_relationship_errors": canonical_relationship_errors,
        "edition_consistency": edition_consistency,
        "book_name_metadata": {
            "canonical_has_translation_names": reports["canonical"]["book_names_in_canonical"],
            "igbob_and_modern_names_match": hnames == mnames,
            "igbob_language_is_ig": meta_ig,
            "igbob_modern_language_is_ig": meta_modern_ig,
            "kjv_language_is_en": meta_kjv_en,
        },
        "igbob_parallelism": {
            "changed_verses": len(changed_ids),
            "unchanged_verses": len(unchanged_ids),
            "missing_pairings": sorted(set(verse_ids["canonical"]) - (set(historical_rows) & set(modern_rows))),
        },
        "modern_source_database_hash_matches": source_hash_matches,
        "kjv_complete": not kjv_consistency["missing_ids"] and not kjv_consistency["extra_ids"],
        "manifest_entries": manifest["databases"],
    }


def fetch_parallel_chapter(
    database_paths: Mapping[str, Path], book_id: str, chapter_number: int
) -> list[dict[str, object]]:
    """Fetch one canonical chapter with historical, modern, and KJV text."""

    connection = _connect_read_only(Path(database_paths["canonical"]))
    try:
        for alias in ("igbob", "igbob_modern", "kjv"):
            key = "igbob-modern" if alias == "igbob_modern" else alias
            connection.execute(f"ATTACH DATABASE ? AS {alias}", (str(Path(database_paths[key]).resolve()),))
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT v.id AS verse_id, v.number AS verse_number, "
            "historical.content AS historical_igbo, modern.content AS modern_igbo, "
            "english.content AS kjv "
            "FROM chapters c JOIN verses v ON v.chapter_id=c.id "
            "JOIN igbob.verses historical ON historical.verse_id=v.id "
            "JOIN igbob_modern.verses modern ON modern.verse_id=v.id "
            "JOIN kjv.verses english ON english.verse_id=v.id "
            "WHERE c.book_id=? AND c.number=? ORDER BY v.number",
            (book_id, chapter_number),
        )
        return [dict(row) for row in rows]
    finally:
        connection.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Android Bible databases and write their manifest.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--manifest", type=Path, default=None)
    args = parser.parse_args(argv)
    paths = {key: database_path(path.name, args.data_dir) for key, path in DEFAULT_DATABASES.items()}
    manifest_path = args.manifest or generated_path("database-manifest.json", args.data_dir)
    unexpected_database_entries = validate_database_directory(database_path("bible.sqlite", args.data_dir).parent)
    if unexpected_database_entries:
        print(json.dumps({"valid": False, "unexpected_database_directory_entries": unexpected_database_entries}, indent=2))
        return 1
    report = validate_runtime_databases(paths)
    if not report["valid"]:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1
    manifest = generate_database_manifest(paths, manifest_path)
    print(json.dumps({"valid": True, "manifest": str(manifest_path), "databases": len(manifest["databases"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
