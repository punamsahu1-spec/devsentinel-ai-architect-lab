import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import vector_rag


TEST_POLICY_TEXT = """
# DevSentinel Security Policy

## Secret Management Policy
Developers must never hardcode passwords, API keys, private keys, or database connection strings in source code.
Secrets must be stored in approved secret managers or environment variables.
If a secret is exposed, it must be removed and rotated immediately.

## Pull Request Security Review Policy
Every pull request must be scanned for leaked secrets before merge.
If critical secrets are found, the merge must be blocked.

## Prompt Injection Policy
AI systems must reject instructions that attempt to override system rules.
Prompt injection attempts must be blocked and logged.
"""


class TestVectorRAG(unittest.TestCase):

    def test_chunk_policy_by_headings(self):
        chunks = vector_rag.chunk_policy_by_headings(TEST_POLICY_TEXT)

        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0]["title"], "Secret Management Policy")
        self.assertIn("hardcode passwords", chunks[0]["content"])

    def test_embed_text_returns_vector(self):
        vocabulary = ["secret", "password", "policy"]
        vector = vector_rag.embed_text("secret password secret", vocabulary)

        self.assertEqual(len(vector), 3)
        self.assertGreater(vector[0], 0)
        self.assertGreater(vector[1], 0)

    def test_retrieve_top_k_policy_chunks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_policy_path = Path(temp_dir) / "security_policy.txt"
            test_index_path = Path(temp_dir) / "policy_vector_index.json"

            test_policy_path.write_text(TEST_POLICY_TEXT, encoding="utf-8")

            with patch.object(vector_rag, "POLICY_PATH", test_policy_path):
                with patch.object(vector_rag, "VECTOR_INDEX_PATH", test_index_path):
                    vector_rag.build_policy_vector_index()

                    results = vector_rag.retrieve_top_k_policy_chunks(
                        query="hardcoded password secret connection string",
                        top_k=2
                    )

                    self.assertEqual(len(results), 2)
                    self.assertEqual(results[0]["title"], "Secret Management Policy")
                    self.assertGreater(results[0]["score"], 0)


if __name__ == "__main__":
    unittest.main()