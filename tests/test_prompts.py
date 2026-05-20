import unittest

from app.prompts import (
    DEVSENTINEL_SYSTEM_PROMPT,
    DEVSENTINEL_JSON_OUTPUT_SCHEMA,
    DEVSENTINEL_USER_PROMPT_TEMPLATE,
    RELEVANCE_GRADER_PROMPT_TEMPLATE,
)


class TestPrompts(unittest.TestCase):

    def test_system_prompt_has_grounding_rules(self):
        self.assertIn("Use only the provided context", DEVSENTINEL_SYSTEM_PROMPT)
        self.assertIn("Do not invent policies", DEVSENTINEL_SYSTEM_PROMPT)
        self.assertIn("Return only valid JSON", DEVSENTINEL_SYSTEM_PROMPT)

    def test_json_schema_has_required_fields(self):
        self.assertIn("decision", DEVSENTINEL_JSON_OUTPUT_SCHEMA)
        self.assertIn("policy_reference", DEVSENTINEL_JSON_OUTPUT_SCHEMA)
        self.assertIn("recommended_next_steps", DEVSENTINEL_JSON_OUTPUT_SCHEMA)

    def test_user_prompt_template_accepts_context(self):
        prompt = DEVSENTINEL_USER_PROMPT_TEMPLATE.format(
            json_schema=DEVSENTINEL_JSON_OUTPUT_SCHEMA,
            context_package='{"decision": "BLOCK"}'
        )

        self.assertIn("Required JSON format", prompt)
        self.assertIn('"decision": "BLOCK"', prompt)

    def test_relevance_grader_prompt_template(self):
        prompt = RELEVANCE_GRADER_PROMPT_TEMPLATE.format(
            finding="password_assign",
            policy_context="Secret Management Policy"
        )

        self.assertIn("relevance grader", prompt)
        self.assertIn("password_assign", prompt)
        self.assertIn("Secret Management Policy", prompt)


if __name__ == "__main__":
    unittest.main()