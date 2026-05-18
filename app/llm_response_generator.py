import json
import os
from typing import Dict, Any

from dotenv import load_dotenv

try:
    from .response_generator import generate_developer_response
except ImportError:
    from response_generator import generate_developer_response

load_dotenv()


def is_gemini_enabled() -> bool:
    """
    Checks whether Gemini LLM response generation is enabled.
    """
    return os.getenv("USE_GEMINI", "false").lower() == "true"


def build_gemini_prompt(context_package: Dict[str, Any]) -> str:
    """
    Builds a strict prompt for Gemini using the curated context package.
    """

    return f"""
You are DevSentinel, an enterprise AI security copilot for pull request safety review.

Use only the provided context.
Do not invent policies.
Do not add facts that are not present in the context.
Return only valid JSON.
Do not wrap the JSON in markdown.

Required JSON format:
{{
  "decision": "ALLOW | BLOCK | HUMAN_REVIEW",
  "reason": "short reason",
  "policy_reference": ["policy section names used"],
  "risk_summary": ["short risk summary"],
  "recommended_next_steps": ["actionable next steps for developer"]
}}

Context:
{json.dumps(context_package, indent=2)}
"""


def parse_gemini_json(text: str) -> Dict[str, Any]:
    """
    Safely parses Gemini response as JSON.
    Handles accidental markdown wrapping.
    """
    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "", 1).strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "", 1).strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return json.loads(cleaned)


def generate_llm_or_fallback_response(context_package: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates response using Gemini if enabled.
    Falls back to local rule-based response if Gemini is disabled or fails.
    """

    if not is_gemini_enabled():
        fallback = generate_developer_response(context_package)
        fallback["response_source"] = "rule_based_fallback"
        return fallback

    try:
        from google import genai

        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        client = genai.Client()
        prompt = build_gemini_prompt(context_package)

        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )

        llm_response = parse_gemini_json(response.text)
        llm_response["response_source"] = "gemini"
        return llm_response

    except Exception as error:
        fallback = generate_developer_response(context_package)
        fallback["response_source"] = "rule_based_fallback"
        fallback["fallback_reason"] = str(error)
        return fallback