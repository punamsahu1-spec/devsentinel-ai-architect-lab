import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import pr_scanner


class TestPRScanner(unittest.TestCase):

    def test_read_diff_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            diff_path = Path(temp_dir) / "pr_diff.txt"
            diff_path.write_text('+ password = "mysecretpassword123"', encoding="utf-8")

            content = pr_scanner.read_diff_file(str(diff_path))

            self.assertIn("password", content)

    def test_pr_scanner_blocks_unsafe_diff(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            diff_path = Path(temp_dir) / "pr_diff.txt"
            diff_path.write_text('+ password = "mysecretpassword123"', encoding="utf-8")

            with patch.object(pr_scanner.sys, "argv", ["pr_scanner.py", str(diff_path)]):
                exit_code = pr_scanner.main()

            self.assertEqual(exit_code, 1)

    def test_pr_scanner_allows_safe_diff(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            diff_path = Path(temp_dir) / "pr_diff.txt"
            diff_path.write_text('+ database_url = os.getenv("DATABASE_URL")', encoding="utf-8")

            with patch.object(pr_scanner.sys, "argv", ["pr_scanner.py", str(diff_path)]):
                exit_code = pr_scanner.main()

            self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()