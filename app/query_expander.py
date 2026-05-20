import json
import os
from typing import Dict, Any, List

from dotenv import load_dotenv

try:
    from .prompts import QUERY_EXPANSION_PROMPT_TEMPLATE
except ImportError:
    from prompts import QUERY_EXPANSION_PROMPT_TEMPLATE


load_dotenv()


DEFAULT_POLICY_TITLES = [
    "Secret Management Policy",
    "Pull Request Security Review Policy",
    "Prompt Injection Policy",
    "Safe Configuration Policy",
    "Human Review Policy",
]


def is_gemini_enabled() -> bool:
    """
    Checks whether Gemini is enabled for query expansion.
    """
    return os.getenv("USE_GEMINI", "false").lower() == "true"


def build_query_expansion_prompt(
    finding_types: List[str],
    base_query: str,
    policy_titles: List[str] | None = None
) -> str:
    """
    Builds the prompt used to ask Gemini for retrieval query expansion.
    """
    if policy_titles is None:
        policy_titles = DEFAULT_POLICY_TITLES

    return QUERY_EXPANSION_PROMPT_TEMPLATE.format(
        finding_types=", ".join(finding_types),
        base_query=base_query,
        policy_titles=", ".join(policy_titles),
    )


def parse_expansion_json(text: str) -> Dict[str, Any]:
    """
    Parses Gemini JSON output safely.
    """
    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "", 1).strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "", 1).strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return json.loads(cleaned)


def deterministic_query_expansion(finding_types: List[str], base_query: str) -> Dict[str, Any]:
    """
    Fallback query expansion without LLM.
    """
    extra_terms = [
        "hardcode passwords",
        "hardcoded credentials",
        "database connection strings",
        "api keys",
        "access tokens",
        "private keys",
        "secret exposed",
        "pull request must be blocked",
        "merge must be blocked",
        "rotated immediately",
        "credential rotation",
        "approved secret manager",
        "environment variables",
    ]

    expanded_query = " ".join([base_query, *extra_terms, *finding_types])

    return {
        "expanded_query": expanded_query,
        "search_concepts": extra_terms,
        "reason": "Used deterministic fallback query expansion.",
        "source": "deterministic_fallback"
    }


def expand_query_with_llm_or_fallback(
    finding_types: List[str],
    base_query: str,
    policy_titles: List[str] | None = None
) -> Dict[str, Any]:
    """
    Uses Gemini to expand retrieval query.
    Falls back to deterministic expansion if Gemini is disabled or fails.
    """
    if not is_gemini_enabled():
        return deterministic_query_expansion(finding_types, base_query)

    try:
        from google import genai

        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        client = genai.Client()

        prompt = build_query_expansion_prompt(
            finding_types=finding_types,
            base_query=base_query,
            policy_titles=policy_titles,
        )

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )

        parsed = parse_expansion_json(response.text)
        parsed["source"] = "gemini"
        return parsed

    except Exception as error:
        fallback = deterministic_query_expansion(finding_types, base_query)
        fallback["fallback_reason"] = str(error)
        return fallback