from typing import Dict, Any, List


def summarize_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Converts raw findings into a compact summary.
    """
    summary = []

    for finding in findings:
        summary.append({
            "type": finding.get("type"),
            "severity": finding.get("severity"),
            "action": finding.get("action")
        })

    return summary


def summarize_recent_memory(recent_memory: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Converts recent memory events into compact context.
    """
    memory_summary = []

    for event in recent_memory:
        memory_summary.append({
            "source": event.get("source"),
            "decision": event.get("decision"),
            "reason": event.get("reason")
        })

    return memory_summary


def summarize_policy_context(policy_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Converts retrieved policy sections into compact context.
    """
    policy_summary = []

    for section in policy_sections:
        policy_summary.append({
            "title": section.get("title"),
            "content": section.get("content"),
            "score": section.get("score")
        })

    return policy_summary


def build_context_package(
    query: str,
    result: Dict[str, Any],
    recent_memory: List[Dict[str, Any]],
    policy_sections: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Builds a clean context package for future LLM/RAG/agentic reasoning.
    """

    context_package = {
        "system_purpose": "DevSentinel is an enterprise AI security copilot for PR safety review.",
        "user_query": query,
        "current_scan": {
            "source": result.get("source"),
            "decision": result.get("decision"),
            "reason": result.get("reason"),
            "findings_summary": summarize_findings(result.get("findings", []))
        },
        "recent_memory_summary": summarize_recent_memory(recent_memory),
        "retrieved_policy_context": summarize_policy_context(policy_sections),
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

    return context_package