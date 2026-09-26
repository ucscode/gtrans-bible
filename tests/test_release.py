from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from builder.release import (
    ReleaseError,
    classify_publication_path,
    load_release_lock,
    load_source_lock,
    prepare_private_backup_manifest,
    validate_recovery_manifest,
    verify_source_inputs,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def minimal_lock(path: Path, source_path: str, expected_hash: str) -> Path:
    lock_path = path / "source-lock.json"
    lock_path.write_text(json.dumps({
        "schema_version": 1,
        "lock_version": 1,
        "sources": [{
            "source_id": "fixture",
            "purpose": "unit test fixture",
            "path": source_path,
            "sha256": expected_hash,
            "required_for_rebuild": True,
            "private_backup_required": True,
        }],
    }), encoding="utf-8")
    return lock_path


class SourceLockTests(unittest.TestCase):
    def test_committed_source_lock_parses_and_contains_no_verse_payload_fields(self):
        path = DATA / "sources" / "source-lock.json"
        lock = load_source_lock(path)
        self.assertEqual(lock["lock_version"], 1)
        self.assertIn("mobobi_apk", {source["source_id"] for source in lock["sources"]})

        def check(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    self.assertNotIn(key.lower(), {"text", "content", "verses", "verse_text"})
                    check(value)
            elif isinstance(node, list):
                for value in node:
                    check(value)

        check(lock)
        for manifest_path in (path, DATA / "releases" / "igbob-modern-v0.5.0.json"):
            raw = manifest_path.read_text(encoding="utf-8")
            self.assertNotIn("Umu Israel we", raw)

    def test_source_hash_validation_passes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "input.bin").write_bytes(b"locked input")
            lock_path = minimal_lock(root, "input.bin", digest(root / "input.bin"))
            result = verify_source_inputs(load_source_lock(lock_path), root)
            self.assertEqual(result[0]["status"], "ok")

    def test_missing_required_input_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock_path = minimal_lock(root, "missing.bin", "0" * 64)
            with self.assertRaisesRegex(ReleaseError, "missing required input"):
                verify_source_inputs(load_source_lock(lock_path), root)

    def test_wrong_source_hash_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "input.bin").write_bytes(b"not the locked input")
            lock_path = minimal_lock(root, "input.bin", "0" * 64)
            with self.assertRaisesRegex(ReleaseError, "SHA-256 mismatch"):
                verify_source_inputs(load_source_lock(lock_path), root)


class ReleaseLockTests(unittest.TestCase):
    def test_release_lock_validates_expected_version_and_content_hash(self):
        release = load_release_lock(DATA / "releases" / "igbob-modern-v0.5.0.json", "0.5.0")
        self.assertEqual(release["modern_content_sha256"], "11cc6bcbb330c2c1f3843cfc74d227c13dfd8f43d8de503f16fad0e02362ac89")
        with self.assertRaisesRegex(ReleaseError, "version mismatch"):
            load_release_lock(DATA / "releases" / "igbob-modern-v0.5.0.json", "0.4.0")

    def test_release_lock_rejects_malformed_schema(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "release.json"
            path.write_text('{"schema_version":99}', encoding="utf-8")
            with self.assertRaisesRegex(ReleaseError, "schema"):
                load_release_lock(path)

    def test_recovery_manifest_loader_checks_count_without_returning_text(self):
        path = DATA / "research" / "igbob-source" / "mobobi-gap-recovery.json"
        if not path.is_file():
            self.skipTest("private recovery input not installed")
        result = validate_recovery_manifest(path)
        self.assertEqual(result["verse_count"], 72)
        self.assertNotIn("text", result)

    def test_private_backup_manifest_hashes_present_required_input_without_copying_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_file = root / "private-source.bin"
            source_file.write_bytes(b"private test input")
            lock_path = minimal_lock(root, "private-source.bin", digest(source_file))
            out = root / "backup.json"
            manifest = prepare_private_backup_manifest(root, lock_path, out)
            self.assertTrue(out.is_file())
            self.assertTrue(manifest["complete"])
            item = next(row for row in manifest["files"] if row["source_id"] == "fixture")
            self.assertEqual(item["sha256"], digest(source_file))
            self.assertEqual(item["size_bytes"], source_file.stat().st_size)
            self.assertEqual(manifest["classification"], "PRIVATE BACKUP INVENTORY; DO NOT COMMIT OR UPLOAD AUTOMATICALLY")


class PublicationClassificationTests(unittest.TestCase):
    def test_publication_classifier_is_conservative(self):
        self.assertEqual(classify_publication_path("builder/release.py"), "SAFE TO COMMIT")
        self.assertEqual(classify_publication_path("data/sources/source-lock.json"), "SAFE TO COMMIT")
        self.assertEqual(classify_publication_path("data/databases/igbob.sqlite"), "MUST REMAIN PRIVATE")
        self.assertEqual(classify_publication_path("data/generated/report.csv"), "GENERATED / OPTIONAL")
        self.assertEqual(classify_publication_path("docs/igbob-research.md"), "UNCERTAIN")
        self.assertEqual(classify_publication_path("random/export.json"), "UNCERTAIN")


class NormalizationRebuildDeterminismTests(unittest.TestCase):
    def test_two_v0_5_rebuilds_have_identical_database_and_logical_hash(self):
        from builder.editions import build_modern_database
        from builder.normalization import Normalizer
        from builder.release import _edition_summary

        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "modern-a.sqlite"
            second = Path(temporary) / "modern-b.sqlite"
            books = {"gen": "GENESIS"}
            verses = {
                "gen-1-1": "In the beginning.",
                "gen-1-2": "tọb͕ọrọ; nē-eme ya.",
                "gen-1-3": "A second deterministic sample.",
            }
            metadata = {"source_database_sha256": "fixture-source-hash", "source_status": "test fixture"}
            build_modern_database(first, books, verses, Normalizer(), metadata)
            build_modern_database(second, books, verses, Normalizer(), metadata)
            first_hash, first_count, first_integrity = _edition_summary(first)
            second_hash, second_count, second_integrity = _edition_summary(second)
            self.assertEqual(first_hash, second_hash)
            self.assertEqual(digest(first), digest(second))
            self.assertEqual((first_count, second_count), (3, 3))
            self.assertEqual((first_integrity, second_integrity), ("ok", "ok"))


if __name__ == "__main__":
    unittest.main()
