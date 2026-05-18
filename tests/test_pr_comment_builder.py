import unittest

from app.pr_comment_builder import build_comment


class TestPRCommentBuilder(unittest.TestCase):

    def test_build_block_comment(self):
        result = {
            "decision": "BLOCK",
            "reason": "Secrets found in PR diff",
            "findings": [
                {
                    "type": "password_assign",
                    "severity": "CRITICAL",
                    "action": "BLOCK_MERGE — remove secret and rotate immediately"
                }
            ]
        }

        comment = build_comment(result)

        self.assertIn("DevSentinel Security Review: BLOCK", comment)
        self.assertIn("password_assign", comment)
        self.assertIn("Required Developer Actions", comment)

    def test_build_allow_comment(self):
        result = {
            "decision": "ALLOW",
            "reason": "No secrets found and query is engineering-related",
            "findings": []
        }

        comment = build_comment(result)

        self.assertIn("DevSentinel Security Review: ALLOW", comment)
        self.assertIn("No hardcoded secrets were detected", comment)


if __name__ == "__main__":
    unittest.main()