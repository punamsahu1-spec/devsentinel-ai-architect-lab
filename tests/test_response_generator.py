import unittest

from app.response_generator import generate_developer_response


class TestResponseGenerator(unittest.TestCase):

    def test_generate_block_response(self):
        context_package = {
            "current_scan": {
                "source": "data/sample_pr_diff.txt",
                "decision": "BLOCK",
                "reason": "Secrets found in PR diff",
                "findings_summary": [
                    {
                        "type": "password_assign",
                        "severity": "CRITICAL",
                        "action": "BLOCK_MERGE — remove secret and rotate immediately"
                    },
                    {
                        "type": "connection_string",
                        "severity": "CRITICAL",
                        "action": "BLOCK_MERGE — remove secret and rotate immediately"
                    }
                ]
            },
            "retrieved_policy_context": [
                {
                    "title": "Secret Management Policy",
                    "content": "Developers must never hardcode passwords.",
                    "score": 3
                },
                {
                    "title": "Pull Request Security Review Policy",
                    "content": "Critical secrets must block merge.",
                    "score": 2
                }
            ]
        }

        response = generate_developer_response(context_package)

        self.assertEqual(response["decision"], "BLOCK")
        self.assertEqual(response["reason"], "Secrets found in PR diff")
        self.assertIn("Secret Management Policy", response["policy_reference"])
        self.assertIn("CRITICAL finding detected: password_assign", response["risk_summary"])
        self.assertIn("Rotate the exposed credential immediately.", response["recommended_next_steps"])

    def test_generate_allow_response(self):
        context_package = {
            "current_scan": {
                "source": "data/safe_pr_diff.txt",
                "decision": "ALLOW",
                "reason": "No secrets found and query is engineering-related",
                "findings_summary": []
            },
            "retrieved_policy_context": [
                {
                    "title": "Safe Configuration Policy",
                    "content": "Applications must read sensitive values from environment variables.",
                    "score": 1
                }
            ]
        }

        response = generate_developer_response(context_package)

        self.assertEqual(response["decision"], "ALLOW")
        self.assertEqual(response["reason"], "No secrets found and query is engineering-related")
        self.assertIn("No hardcoded secrets were detected in the scanned PR diff.", response["risk_summary"])
        self.assertIn("Continue with standard code review and CI checks.", response["recommended_next_steps"])

    def test_generate_human_review_response(self):
        context_package = {
            "current_scan": {
                "source": "data/unknown_pr_diff.txt",
                "decision": "HUMAN_REVIEW",
                "reason": "Risk could not be determined automatically",
                "findings_summary": []
            },
            "retrieved_policy_context": [
                {
                    "title": "Human Review Policy",
                    "content": "Uncertain risks should be routed to human review.",
                    "score": 2
                }
            ]
        }

        response = generate_developer_response(context_package)

        self.assertEqual(response["decision"], "HUMAN_REVIEW")
        self.assertEqual(response["reason"], "Risk could not be determined automatically")
        self.assertIn("Human Review Policy", response["policy_reference"])
        self.assertIn("Route the PR to a security reviewer.", response["recommended_next_steps"])


if __name__ == "__main__":
    unittest.main()