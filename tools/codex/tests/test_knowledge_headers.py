import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "knowledge_headers", Path(__file__).resolve().parents[1] / "knowledge_headers.py"
)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class HeaderTests(unittest.TestCase):
    def test_environment_credential_takes_precedence_over_file(self):
        with patch.dict(os.environ, {"KNOWLEDGE_TOKEN": "test-env-token"}, clear=True):
            self.assertEqual(helper.read_headers("/missing"), {"Authorization": "Bearer test-env-token"})

    def test_private_token_file_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            path = Path(directory) / "token"
            path.write_text("test-file-token\n")
            path.chmod(0o600)
            self.assertEqual(helper.read_headers(path), {"Authorization": "Bearer test-file-token"})

    def test_shared_token_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            path = Path(directory) / "token"
            path.write_text("test-file-token")
            path.chmod(0o644)
            with self.assertRaisesRegex(ValueError, "mode 600"):
                helper.read_headers(path)

    def test_header_injection_is_rejected(self):
        with patch.dict(os.environ, {"KNOWLEDGE_TOKEN": "test\r\nInjected: header"}, clear=True):
            with self.assertRaisesRegex(ValueError, "whitespace"):
                helper.read_headers()


if __name__ == "__main__":
    unittest.main()
