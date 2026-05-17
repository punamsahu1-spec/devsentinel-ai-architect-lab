import unittest

from app.context_builder import build_context_package


class TestContextBuilder(unittest.TestCase):

    def test_build_context_package_for_blocked_pr(self):
        query = "Can you review this API deployment error before merge?"

        result = {
            "source": "data/sample_pr_diff.txt",
            "decision": "BLOCK",
            "reason": "Secrets found in PR diff",
            "findings": [
                {
                    "type": "password_assign",
                    "count": 1,
                    "severity": "CRITICAL",
                    "action": "BLOCK_MERGE — remove secret and rotate immediately"
                }
            ]
        }

        recent_memory = [
            {
                "source": "data/sample_pr_diff.txt",
                "decision": "BLOCK",
                "reason": "Secrets found in PR diff"
            }
        ]

        policy_sections = [
            {
                "title": "Secret Management Policy",
                "content": "Developers must never hardcode passwords or database connection strings.",
                "score": 3
            }
        ]

        context = build_context_package(query, result, recent_memory, policy_sections)

        self.assertEqual(
            context["system_purpose"],
            "DevSentinel is an enterprise AI security copilot for PR safety review."
        )

        self.assertEqual(context["user_query"], query)
        self.assertEqual(context["current_scan"]["decision"], "BLOCK")
        self.assertEqual(context["current_scan"]["reason"], "Secrets found in PR diff")
        self.assertEqual(context["current_scan"]["findings_summary"][0]["type"], "password_assign")
        self.assertEqual(context["recent_memory_summary"][0]["decision"], "BLOCK")
        self.assertEqual(context["retrieved_policy_context"][0]["title"], "Secret Management Policy")
        self.assertIn("policy_reference", context["response_instruction"]["must_include"])
        self.assertIn("recommended_next_steps", context["response_instruction"]["must_include"])


if __name__ == "__main__":
    unittest.main()