from typing import Dict, Any, List


def format_policy_references(policy_sections: List[Dict[str, Any]]) -> List[str]:
    """
    Converts retrieved policy sections into simple policy references.
    """
    references = []

    for section in policy_sections:
        title = section.get("title", "Unknown Policy")
        references.append(title)

    return references


def generate_developer_response(context_package: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a policy-grounded developer response without using an LLM.

    Later, this can be replaced or enhanced with Gemini 2.5 Flash free tier.
    """
    current_scan = context_package.get("current_scan", {})
    decision = current_scan.get("decision", "HUMAN_REVIEW")
    reason = current_scan.get("reason", "No reason provided")
    findings = current_scan.get("findings_summary", [])
    policy_sections = context_package.get("retrieved_policy_context", [])

    policy_references = format_policy_references(policy_sections)

    if decision == "BLOCK":
        risk_summary = [
            f"{finding.get('severity', 'UNKNOWN')} finding detected: {finding.get('type')}"
            for finding in findings
        ]

        recommended_next_steps = [
            "Remove the hardcoded secret from the code.",
            "Move the value to an environment variable or approved secret manager.",
            "Rotate the exposed credential immediately.",
            "Rerun the PR scan after fixing the issue.",
            "Request human review if the credential may have reached a shared branch or public repository."
        ]

    elif decision == "ALLOW":
        risk_summary = [
            "No hardcoded secrets were detected in the scanned PR diff."
        ]

        recommended_next_steps = [
            "Continue with standard code review and CI checks.",
            "Ensure secrets continue to be loaded from environment variables or approved secret stores."
        ]

    else:
        risk_summary = [
            "The risk could not be fully determined automatically."
        ]

        recommended_next_steps = [
            "Route the PR to a security reviewer.",
            "Review the retrieved policy context before approving merge."
        ]

    return {
        "decision": decision,
        "reason": reason,
        "policy_reference": policy_references,
        "risk_summary": risk_summary,
        "recommended_next_steps": recommended_next_steps
    }