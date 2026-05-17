import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import memory_store


class TestMemoryStore(unittest.TestCase):

    def test_add_scan_event_and_recent_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_memory_path = Path(temp_dir) / "memory.json"

            with patch.object(memory_store, "MEMORY_PATH", test_memory_path):
                memory_store.add_scan_event(
                    source="data/sample_pr_diff.txt",
                    decision="BLOCK",
                    reason="Secrets found in PR diff",
                    findings=[
                        {
                            "type": "password_assign",
                            "severity": "CRITICAL",
                            "action": "BLOCK_MERGE"
                        }
                    ]
                )

                recent_history = memory_store.get_recent_scan_history(limit=1)

                self.assertEqual(len(recent_history), 1)
                self.assertEqual(recent_history[0]["decision"], "BLOCK")

                memory = memory_store.load_memory()

                self.assertEqual(len(memory["scan_history"]), 1)
                self.assertEqual(len(memory["known_risks"]), 1)
                self.assertEqual(memory["known_risks"][0]["finding_types"], ["password_assign"])

    def test_corrupted_memory_resets_safely(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_memory_path = Path(temp_dir) / "memory.json"
            test_memory_path.write_text("{ invalid json", encoding="utf-8")

            with patch.object(memory_store, "MEMORY_PATH", test_memory_path):
                memory = memory_store.load_memory()

                self.assertEqual(memory["scan_history"], [])
                self.assertEqual(memory["known_risks"], [])
                self.assertEqual(memory["team_patterns"], [])

                saved_memory = json.loads(test_memory_path.read_text(encoding="utf-8"))
                self.assertEqual(saved_memory["scan_history"], [])


if __name__ == "__main__":
    unittest.main()