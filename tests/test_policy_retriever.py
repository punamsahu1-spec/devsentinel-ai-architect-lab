import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import policy_retriever


TEST_POLICY_TEXT = """
# DevSentinel Security Policy

## Secret Management Policy
Developers must never hardcode passwords, API keys, private keys, or database connection strings in source code.
Secrets must be stored in approved secret managers or environment variables.
If a secret is exposed in a pull request, the pull request must be blocked.
The exposed credential must be removed from code and rotated immediately.

## Pull Request Security Review Policy
Every pull request must be scanned for leaked secrets before merge.
If critical secrets are found, the merge must be blocked.

## Prompt Injection Policy
AI systems must reject instructions that attempt to override system rules.
Prompt injection attempts must be blocked and logged.
"""


class TestPolicyRetriever(unittest.TestCase):

    def test_split_policy_into_sections(self):
        sections = policy_retriever.split_policy_into_sections(TEST_POLICY_TEXT)

        self.assertEqual(len(sections), 3)
        self.assertEqual(sections[0]["title"], "Secret Management Policy")
        self.assertIn("hardcode passwords", sections[0]["content"])

    def test_retrieve_policy_sections_for_secret_terms(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_policy_path = Path(temp_dir) / "security_policy.txt"
            test_policy_path.write_text(TEST_POLICY_TEXT, encoding="utf-8")

            with patch.object(policy_retriever, "POLICY_PATH", test_policy_path):
                sections = policy_retriever.retrieve_policy_sections(
                    query_terms=["secret", "password", "connection string"],
                    top_k=2
                )

                self.assertGreaterEqual(len(sections), 1)
                self.assertEqual(sections[0]["title"], "Secret Management Policy")
                self.assertGreater(sections[0]["score"], 0)

    def test_get_policy_for_secret_findings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_policy_path = Path(temp_dir) / "security_policy.txt"
            test_policy_path.write_text(TEST_POLICY_TEXT, encoding="utf-8")

            findings = [
                {
                    "type": "password_assign",
                    "severity": "CRITICAL",
                    "action": "BLOCK_MERGE"
                }
            ]

            with patch.object(policy_retriever, "POLICY_PATH", test_policy_path):
                sections = policy_retriever.get_policy_for_findings(findings)

                self.assertGreaterEqual(len(sections), 1)
                section_titles = [section["title"] for section in sections]
                self.assertIn("Secret Management Policy", section_titles)

    def test_default_policy_retrieval_when_no_findings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_policy_path = Path(temp_dir) / "security_policy.txt"
            test_policy_path.write_text(TEST_POLICY_TEXT, encoding="utf-8")

            with patch.object(policy_retriever, "POLICY_PATH", test_policy_path):
                sections = policy_retriever.get_policy_for_findings([])

                self.assertGreaterEqual(len(sections), 1)


if __name__ == "__main__":
    unittest.main()