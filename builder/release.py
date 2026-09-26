"""Source locking, private backup inventory, and deterministic local releases."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from .database import build_databases, validate_oicb_database, validate_structure_database
from .editions import (
    _content_sha256,
    import_kjv_dataset,
    normalize_edition_database,
    validate_edition_database,
)
from .mobobi_import import import_mobobi_apk
from .pipeline import extract_archive, sha256_file
from .normalization import Normalizer
from .usfm import parse_source_directory, validate_bible


LOCK_SCHEMA_VERSION = 1


class ReleaseError(RuntimeError):
    """An input, lock, or output did not meet release requirements."""


def load_source_lock(path: Path) -> dict[str, Any]:
    try:
        lock = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"cannot read source lock {path}: {exc}") from exc
    if not isinstance(lock, dict) or lock.get("schema_version") != LOCK_SCHEMA_VERSION:
        raise ReleaseError("unsupported or malformed source-lock schema")
    sources = lock.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ReleaseError("source lock must contain a non-empty sources list")
    seen: set[str] = set()
    required_fields = {"source_id", "path", "sha256", "required_for_rebuild", "private_backup_required"}
    for entry in sources:
        if not isinstance(entry, dict) or not required_fields <= entry.keys():
            raise ReleaseError("source lock contains an incomplete source entry")
        source_id = entry["source_id"]
        if not isinstance(source_id, str) or not source_id or source_id in seen:
            raise ReleaseError("source lock has a missing or duplicate source_id")
        seen.add(source_id)
        if not isinstance(entry["sha256"], str) or len(entry["sha256"]) != 64:
            raise ReleaseError(f"source {source_id} has no valid SHA-256")
        PurePosixPath(entry["path"])
        if PurePosixPath(entry["path"]).is_absolute() or ".." in PurePosixPath(entry["path"]).parts:
            raise ReleaseError(f"source {source_id} path must stay inside the data directory")
        if not isinstance(entry["required_for_rebuild"], bool) or not isinstance(entry["private_backup_required"], bool):
            raise ReleaseError(f"source {source_id} has invalid boolean flags")
    return lock


def verify_source_inputs(lock: dict[str, Any], data_dir: Path, *, required_only: bool = False) -> list[dict[str, Any]]:
    """Verify locked files; missing required files and any present hash mismatch fail closed."""
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for entry in lock["sources"]:
        if required_only and not entry["required_for_rebuild"]:
            continue
        path = data_dir / entry["path"]
        exists = path.is_file()
        if not exists:
            result = {"source_id": entry["source_id"], "path": entry["path"], "status": "missing"}
            results.append(result)
            if entry["required_for_rebuild"]:
                errors.append(f"missing required input {entry['source_id']}: {path}")
            continue
        digest = sha256_file(path)
        status = "ok" if digest == entry["sha256"] else "hash_mismatch"
        results.append({"source_id": entry["source_id"], "path": entry["path"], "status": status, "sha256": digest})
        if status != "ok":
            errors.append(f"SHA-256 mismatch for {entry['source_id']}: expected {entry['sha256']}, got {digest}")
    if errors:
        raise ReleaseError("source verification failed:\n- " + "\n- ".join(errors))
    return results


def load_release_lock(path: Path, expected_version: str | None = None) -> dict[str, Any]:
    try:
        lock = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"cannot read release lock {path}: {exc}") from exc
    if not isinstance(lock, dict) or lock.get("schema_version") != LOCK_SCHEMA_VERSION:
        raise ReleaseError("unsupported or malformed release-lock schema")
    if expected_version is not None and lock.get("release_version") != expected_version:
        raise ReleaseError(f"release lock version mismatch: expected {expected_version}, found {lock.get('release_version')}")
    for key in ("release_version", "historical_source_database_sha256", "normalization_ruleset_version",
                "reviewed_lexicon_version", "expected_verse_count", "expected_changed_verse_count",
                "expected_transformation_count", "modern_content_sha256", "artifacts"):
        if key not in lock:
            raise ReleaseError(f"release lock missing required field {key!r}")
    if not isinstance(lock["artifacts"], dict):
        raise ReleaseError("release lock artifacts must be an object")
    modern = lock["artifacts"].get("igbob-modern.sqlite", {})
    structure = lock["artifacts"].get("bible.sqlite", {})
    historical = lock["artifacts"].get("igbob.sqlite", {})
    if (lock.get("database_sha256") != modern.get("database_sha256")
            or lock.get("modern_content_sha256") != modern.get("logical_content_sha256")
            or lock.get("canonical_structure_sha256") != structure.get("logical_sha256")
            or lock.get("historical_source_database_sha256") != historical.get("database_sha256")):
        raise ReleaseError("release lock top-level hashes disagree with artifact records")
    return lock


def _structure_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with sqlite3.connect(path) as connection:
        for table, query in (
            ("books", "SELECT id,position FROM books ORDER BY position"),
            ("chapters", "SELECT id,book_id,number FROM chapters ORDER BY book_id,number"),
            ("verses", "SELECT id,chapter_id,number FROM verses ORDER BY chapter_id,number"),
        ):
            digest.update(table.encode("ascii") + b"\0")
            for row in connection.execute(query):
                for value in row:
                    encoded = str(value).encode("utf-8")
                    digest.update(len(encoded).to_bytes(8, "big"))
                    digest.update(encoded)
    return digest.hexdigest()


def _edition_summary(path: Path) -> tuple[str, int, str]:
    with sqlite3.connect(path) as connection:
        rows = dict(connection.execute("SELECT verse_id,content FROM verses"))
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    return _content_sha256(rows), len(rows), integrity


def validate_recovery_manifest(path: Path, expected_count: int = 72) -> dict[str, Any]:
    """Validate recovery IDs and provenance without echoing or returning verse text."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"cannot read private recovery manifest: {exc}") from exc
    verses = data.get("verses") if isinstance(data, dict) else None
    urls = data.get("witness_urls") if isinstance(data, dict) else None
    if not isinstance(verses, dict) or len(verses) != expected_count:
        raise ReleaseError(f"recovery manifest expected {expected_count} verses")
    if not isinstance(urls, dict):
        raise ReleaseError("recovery manifest is missing witness URL metadata")
    for verse_id, entry in verses.items():
        if (not isinstance(verse_id, str) or not isinstance(entry, dict)
                or not isinstance(entry.get("text"), str) or not entry["text"].strip()
                or not isinstance(entry.get("source_witness"), str) or not entry["source_witness"].strip()):
            raise ReleaseError(f"invalid recovery verse record for {verse_id!r}")
    return {"verse_count": len(verses), "witness_count": len(urls), "verse_ids": sorted(verses)}


def classify_publication_path(relative_path: str) -> str:
    """Conservative path-level publication classification used by docs/tests."""
    path = PurePosixPath(relative_path)
    value = path.as_posix()
    if value in {".env"} or value.startswith(("data/databases/", "data/research/", "data/private-source/",
                                               "data/downloads/", "data/extracted/", "data/generated/")):
        return "MUST REMAIN PRIVATE" if not value.startswith("data/generated/") else "GENERATED / OPTIONAL"
    if path.suffix.lower() in {".sqlite", ".apk", ".pdf", ".usfm", ".djvu", ".xml"}:
        return "MUST REMAIN PRIVATE"
    if value == "docs/igbob-research.md":
        return "UNCERTAIN"
    if value in {"data/sources/source-lock.json", "data/releases/igbob-modern-v0.5.0.json"}:
        return "SAFE TO COMMIT"
    if value.startswith(("builder/", "tests/", "normalization/", "docs/")) or value in {
        "README.md", "AGENTS.md", ".gitignore", "pyproject.toml"
    }:
        return "SAFE TO COMMIT"
    return "UNCERTAIN"


def _safe_extract(archive_path: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        root = destination.resolve()
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if root not in target.parents and target != root:
                raise ReleaseError(f"unsafe path in source archive: {member.filename}")
        archive.extractall(destination)
    usfm = sorted(destination.rglob("*.usfm"))
    if not usfm:
        raise ReleaseError(f"no USFM source files found in {archive_path}")
    return usfm[0].parent


def _atomic_publish_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w+b", delete=False, dir=destination.parent,
                                     prefix=f".{destination.name}.") as handle:
        temporary = Path(handle.name)
    try:
        shutil.copyfile(source, temporary)
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def rebuild_release(data_dir: Path, source_lock_path: Path, release_lock_path: Path, version: str) -> dict[str, Any]:
    """Rebuild all locked primary databases in isolation and publish after validation."""
    data_dir = Path(data_dir)
    lock = load_source_lock(source_lock_path)
    release = load_release_lock(release_lock_path, version)
    if release.get("required_source_lock_version") != lock.get("lock_version"):
        raise ReleaseError("release lock requires a different source-lock version")
    verify_source_inputs(lock, data_dir, required_only=True)
    by_id = {entry["source_id"]: data_dir / entry["path"] for entry in lock["sources"]}
    required_ids = ("oicb_archive", "kjv_archive", "mobobi_apk", "gap_recovery", "normalization_rules", "reviewed_lexicon")
    missing_entries = [source_id for source_id in required_ids if source_id not in by_id]
    if missing_entries:
        raise ReleaseError(f"source lock missing rebuild inputs: {', '.join(missing_entries)}")
    locked_sources = {entry["source_id"]: entry for entry in lock["sources"]}
    for source_id, release_key in (("normalization_rules", "normalization_rules_sha256"),
                                   ("reviewed_lexicon", "reviewed_lexicon_sha256"),
                                   ("gap_recovery", "recovery_manifest")):
        expected = release[release_key] if release_key != "recovery_manifest" else release[release_key]["sha256"]
        if locked_sources[source_id]["sha256"] != expected:
            raise ReleaseError(f"release lock and source lock disagree for {source_id}")
    validate_recovery_manifest(by_id["gap_recovery"], expected_count=72)

    with tempfile.TemporaryDirectory(prefix="igbob-release-") as temp_name:
        stage = Path(temp_name)
        staged_data = stage / "data"
        dbdir = staged_data / "databases"
        dbdir.mkdir(parents=True)

        oicb_source = extract_archive(by_id["oicb_archive"], staged_data / "extracted" / "oicb")
        parsed = parse_source_directory(oicb_source)
        validate_bible(parsed)
        build_databases(parsed, dbdir / "bible.sqlite", dbdir / "oicb.sqlite")

        kjv_source = _safe_extract(by_id["kjv_archive"], staged_data / "extracted" / "kjv")
        import_kjv_dataset(kjv_source, dbdir / "bible.sqlite", dbdir / "kjv.sqlite")

        recovery_entry = next(e for e in lock["sources"] if e["source_id"] == "gap_recovery")
        report_path = staged_data / "generated" / "igbob-import-report.json"
        import_mobobi_apk(by_id["mobobi_apk"], dbdir / "bible.sqlite", dbdir / "igbob.sqlite",
                          report_path=report_path, kjv_path=dbdir / "kjv.sqlite", recovery_path=by_id["gap_recovery"])
        validate_edition_database(dbdir / "igbob.sqlite", dbdir / "bible.sqlite", require_complete=True)
        normalizer = Normalizer(ruleset_path=by_id["normalization_rules"], lexicon_path=by_id["reviewed_lexicon"])
        normalization = normalize_edition_database(
            dbdir / "igbob.sqlite", dbdir / "igbob-modern.sqlite",
            audit_report_path=staged_data / "generated" / "igbob-normalization-audit.json",
            unresolved_forms_path=None,
            normalizer=normalizer,
        )
        if normalizer.ruleset_version != release["normalization_ruleset_version"]:
            raise ReleaseError("normalization ruleset version does not match release lock")
        if normalizer.lexicon_version != release["reviewed_lexicon_version"]:
            raise ReleaseError("reviewed lexicon version does not match release lock")

        with sqlite3.connect(dbdir / "igbob-modern.sqlite") as connection:
            modern_meta = dict(connection.execute("SELECT key,value FROM metadata"))
        source_db_hash = sha256_file(dbdir / "igbob.sqlite")
        if source_db_hash != release["historical_source_database_sha256"]:
            raise ReleaseError(f"historical source database SHA-256 mismatch: expected {release['historical_source_database_sha256']}, got {source_db_hash}")
        content_hash, count, integrity = _edition_summary(dbdir / "igbob-modern.sqlite")
        if integrity != "ok":
            raise ReleaseError(f"modern database integrity check failed: {integrity}")
        if count != release["expected_verse_count"] or content_hash != release["modern_content_sha256"]:
            raise ReleaseError(f"modern logical release mismatch: count={count}, content_sha256={content_hash}")
        if int(modern_meta["changed_verse_count"]) != release["expected_changed_verse_count"]:
            raise ReleaseError("modern changed-verse count does not match release lock")
        if int(modern_meta["transformation_count"]) != release["expected_transformation_count"]:
            raise ReleaseError("modern transformation count does not match release lock")

        expected_outputs = release["artifacts"]
        observed: dict[str, dict[str, Any]] = {}
        for filename in ("bible.sqlite", "kjv.sqlite", "igbob.sqlite", "igbob-modern.sqlite"):
            path = dbdir / filename
            with sqlite3.connect(path) as connection:
                integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
            if integrity != "ok":
                raise ReleaseError(f"{filename} integrity check failed: {integrity}")
            item: dict[str, Any] = {"database_sha256": sha256_file(path), "integrity": integrity}
            if filename == "bible.sqlite":
                validate_structure_database(path)
                item["logical_sha256"] = _structure_sha256(path)
            else:
                validate_edition_database(path, dbdir / "bible.sqlite", require_complete=True)
                item["logical_content_sha256"], item["verse_count"], _ = _edition_summary(path)
            expected = expected_outputs[filename]
            logical_key = "logical_sha256" if filename == "bible.sqlite" else "logical_content_sha256"
            if item[logical_key] != expected[logical_key]:
                raise ReleaseError(f"{filename} logical hash mismatch: expected {expected[logical_key]}, got {item[logical_key]}")
            item["database_sha256_matches_lock"] = item["database_sha256"] == expected["database_sha256"]
            observed[filename] = item
        validate_oicb_database(dbdir / "oicb.sqlite", dbdir / "bible.sqlite")

        # Exact content is the release identity. SQLite binary differences are reported,
        # since SQLite version/compile details can affect bytes without changing rows.
        for filename in ("bible.sqlite", "oicb.sqlite", "igbob.sqlite", "igbob-modern.sqlite", "kjv.sqlite"):
            destination = data_dir / "databases" / filename
            _atomic_publish_file(dbdir / filename, destination)
        return {
            "release_version": version,
            "normalization": normalization,
            "modern_content_sha256": content_hash,
            "modern_content_sha256_matches_lock": content_hash == release["modern_content_sha256"],
            "artifacts": observed,
            "published_to": str(data_dir / "databases"),
        }


def prepare_private_backup_manifest(data_dir: Path, source_lock_path: Path, output_path: Path) -> dict[str, Any]:
    lock = load_source_lock(source_lock_path)
    entries: list[dict[str, Any]] = []
    missing_required: list[str] = []
    for source in lock["sources"]:
        if not source["private_backup_required"]:
            continue
        path = Path(data_dir) / source["path"]
        item: dict[str, Any] = {
            "relative_path": source["path"], "purpose": source["purpose"],
            "required": bool(source["required_for_rebuild"]), "source_id": source["source_id"],
        }
        if path.is_file():
            item.update(size_bytes=path.stat().st_size, sha256=sha256_file(path), status="present",
                        expected_sha256_matches=sha256_file(path) == source["sha256"])
            if not item["expected_sha256_matches"]:
                raise ReleaseError(f"private backup input hash mismatch: {path}")
        else:
            item.update(status="missing", size_bytes=None, sha256=None)
            if item["required"]:
                missing_required.append(source["path"])
        entries.append(item)
    for filename in ("bible.sqlite", "igbob.sqlite", "igbob-modern.sqlite", "kjv.sqlite"):
        path = Path(data_dir) / "databases" / filename
        item = {"relative_path": f"databases/{filename}", "purpose": "generated local database backup",
                "required": filename in {"igbob.sqlite", "igbob-modern.sqlite"}, "source_id": "generated:" + filename}
        if path.is_file():
            item.update(size_bytes=path.stat().st_size, sha256=sha256_file(path), status="present")
        else:
            item.update(status="missing", size_bytes=None, sha256=None)
        entries.append(item)
    manifest = {
        "manifest_version": 1, "classification": "PRIVATE BACKUP INVENTORY; DO NOT COMMIT OR UPLOAD AUTOMATICALLY",
        "complete": not missing_required,
        "missing_required_paths": missing_required,
        "instructions": "Copy every present required/private file to approved external private storage; rerun this command to verify its hash.",
        "files": entries,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest
