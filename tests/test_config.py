import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from builder.config import load_repository_env, resolve_project_id


class ConfigTests(unittest.TestCase):
    def test_dotenv_loading_precedence_and_relative_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text(
                "GOOGLE_CLOUD_PROJECT=from-dotenv\n"
                "GOOGLE_APPLICATION_CREDENTIALS=secrets/account.json\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {}, clear=True):
                self.assertEqual(load_repository_env(root), root / ".env")
                self.assertEqual(os.environ["GOOGLE_CLOUD_PROJECT"], "from-dotenv")
                self.assertEqual(os.environ["GOOGLE_APPLICATION_CREDENTIALS"], str(root / "secrets/account.json"))

            with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "from-process"}, clear=True):
                load_repository_env(root)
                self.assertEqual(os.environ["GOOGLE_CLOUD_PROJECT"], "from-process")

    def test_cli_project_precedes_environment_and_env_is_ignored(self):
        with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "from-process"}, clear=True):
            self.assertEqual(resolve_project_id("from-cli"), "from-cli")
            self.assertEqual(resolve_project_id(), "from-process")
        self.assertIn(".env", Path(".gitignore").read_text(encoding="utf-8"))
