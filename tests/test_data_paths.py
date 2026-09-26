from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from builder.android_database import DEFAULT_DATABASES, validate_database_directory
from builder.data_paths import DATABASE_FILENAMES, database_path, database_paths, generated_path
from builder.cli import _paths, _translation_paths


class DataPathTests(unittest.TestCase):
    def test_all_database_artifacts_resolve_under_one_database_directory(self):
        root = Path("/tmp/path-test-data")
        paths = database_paths(root)
        self.assertEqual(set(paths.values()), {database_path(name, root) for name in DATABASE_FILENAMES})
        self.assertTrue(all(path.parent == root / "databases" and path.suffix == ".sqlite" for path in paths.values()))
        self.assertEqual(
            DEFAULT_DATABASES,
            {key: database_path(name) for key, name in {
                "canonical": "bible.sqlite", "igbob": "igbob.sqlite",
                "igbob-modern": "igbob-modern.sqlite", "kjv": "kjv.sqlite",
            }.items()},
        )
        self.assertEqual(generated_path("report.json", root), root / "generated" / "report.json")
        pipeline_paths = _paths(root)
        self.assertEqual(pipeline_paths[2:], (database_path("bible.sqlite", root), database_path("oicb.sqlite", root)))
        self.assertEqual(
            _translation_paths(root),
            (database_path("bible.sqlite", root), database_path("oicb.sqlite", root),
             database_path("oicb-google-en.sqlite", root)),
        )

    def test_database_directory_accepts_only_flat_sqlite_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bible.sqlite").touch()
            self.assertEqual(validate_database_directory(root), [])
            (root / "report.json").touch()
            (root / "nested").mkdir()
            self.assertEqual(validate_database_directory(root), ["nested", "report.json"])


if __name__ == "__main__":
    unittest.main()
