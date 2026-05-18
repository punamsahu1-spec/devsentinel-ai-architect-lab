import json
import os
import unittest
from unittest.mock import patch

from app.llm_response_generator import (
    build_gemini_prompt,
    generate_llm_or_fallback_response,
    parse_gemini_json,
)


class TestLLMResponseGenerator(unittest.TestCase):

    def sample_context_package(self):
        return {
            "system_purpose": "DevSentinel is an enterprise AI security copilot for PR safety review.",
            "user_query": "Can you review this API deployment error before merge?",
            "current_scan": {
                "source": "data/sample_pr_diff.txt",
                "decision": "BLOCK",
                "reason": "Secrets found in PR diff",
                "findings_summary": [
                    {
                        "type": "password_assign",
                        "severity": "CRITICAL",
                        "action": "BLOCK_MERGE — remove secret and rotate immediately"
                    }
                ]
            },
            "recent_memory_summary": [],
            "retrieved_policy_context": [
                {
                    "title": "Secret Management Policy",
                    "content": "Developers must never hardcode passwords.",
                    "score": 3
                }
            ],
            "response_instruction": {
                "style": "Be concise, actionable, and security-focused.",
                "grounding_rule": "Use retrieved policy context when explaining the decision.",
                "allowed_decisions": ["ALLOW", "BLOCK", "HUMAN_REVIEW"],
                "must_include": [
                    "decision",
                    "reason",
                    "policy_reference",
                    "risk_summary",
                    "recommended_next_steps"
                ]
            }
        }

    def test_build_gemini_prompt_contains_context(self):
        context_package = self.sample_context_package()

        prompt = build_gemini_prompt(context_package)

        self.assertIn("DevSentinel", prompt)
        self.assertIn("Return only valid JSON", prompt)
        self.assertIn("Secret Management Policy", prompt)
        self.assertIn("password_assign", prompt)

    def test_parse_gemini_json_plain_json(self):
        response_text = json.dumps({
            "decision": "BLOCK",
            "reason": "Secrets found",
            "policy_reference": ["Secret Management Policy"],
            "risk_summary": ["Critical secret found"],
            "recommended_next_steps": ["Remove secret"]
        })

        parsed = parse_gemini_json(response_text)

        self.assertEqual(parsed["decision"], "BLOCK")
        self.assertEqual(parsed["policy_reference"], ["Secret Management Policy"])

    def test_parse_gemini_json_markdown_wrapped(self):
        response_text = """```json
{
  "decision": "BLOCK",
  "reason": "Secrets found",
  "policy_reference": ["Secret Management Policy"],
  "risk_summary": ["Critical secret found"],
  "recommended_next_steps": ["Remove secret"]
}
```"""

        parsed = parse_gemini_json(response_text)

        self.assertEqual(parsed["decision"], "BLOCK")
        self.assertIn("Remove secret", parsed["recommended_next_steps"])

    def test_fallback_when_gemini_disabled(self):
        context_package = self.sample_context_package()

        with patch.dict(os.environ, {"USE_GEMINI": "false"}):
            response = generate_llm_or_fallback_response(context_package)

        self.assertEqual(response["decision"], "BLOCK")
        self.assertEqual(response["response_source"], "rule_based_fallback")
        self.assertIn("Secret Management Policy", response["policy_reference"])


if __name__ == "__main__":
    unittest.main()