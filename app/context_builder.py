from typing import Dict, Any, List


def summarize_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Converts raw findings into a compact summary.

    This is useful because LLMs should receive only the important details,
    not unnecessary raw scanner output.
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

    This helps the AI understand repeated patterns without reading full logs.
    """
    memory_summary = []

    for event in recent_memory:
        memory_summary.append({
            "source": event.get("source"),
            "decision": event.get("decision"),
            "reason": event.get("reason")
        })

    return memory_summary


def build_context_package(
    query: str,
    result: Dict[str, Any],
    recent_memory: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Builds a clean context package for future LLM/RAG/agentic reasoning.

    This is the core context engineering step.
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
        "response_instruction": {
            "style": "Be concise, actionable, and security-focused.",
            "allowed_decisions": ["ALLOW", "BLOCK", "HUMAN_REVIEW"],
            "must_include": [
                "decision",
                "reason",
                "risk_summary",
                "recommended_next_steps"
            ]
        }
    }

    return context_package