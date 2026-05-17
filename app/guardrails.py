import re
from typing import Tuple, List, Dict


SECRET_PATTERNS = {
    "aws_key": r"AKIA[0-9A-Z]{16}",
    "google_api_key": r"AIza[0-9A-Za-z\-_]{35}",
    "github_token": r"ghp_[0-9a-zA-Z]{36}",
    "private_key": r"-----BEGIN (RSA |EC )?PRIVATE KEY-----",
    "password_assign": r"(password|passwd|pwd|secret|api_key)\s*=\s*['\"][^'\"]{8,}['\"]",
    "connection_string": r"(mongodb|postgresql|mysql):\/\/[^:]+:[^@]+@",
}


def scan_diff_for_secrets(diff_text: str) -> Tuple[bool, List[Dict]]:
    """
    Scans code or PR diff text for leaked secrets.

    Returns:
    - True/False if secrets are found
    - List of findings
    """
    findings = []

    for secret_type, pattern in SECRET_PATTERNS.items():
        matches = re.findall(pattern, diff_text, re.IGNORECASE)

        if matches:
            findings.append({
                "type": secret_type,
                "count": len(matches),
                "severity": "CRITICAL",
                "action": "BLOCK_MERGE — remove secret and rotate immediately"
            })

    return len(findings) > 0, findings


def validate_engineering_scope(query: str) -> Tuple[bool, str]:
    """
    Blocks prompt injection and non-engineering queries.
    """
    injection_patterns = [
        "ignore previous",
        "forget previous",
        "forget all instructions",
        "you are now",
        "act as",
        "bypass",
        "override system"
    ]

    for pattern in injection_patterns:
        if pattern in query.lower():
            return False, "Prompt injection detected"

    engineering_keywords = [
        "code", "function", "bug", "error", "deploy", "service", "api",
        "database", "pr", "merge", "test", "build", "pipeline", "incident",
        "latency", "memory", "timeout", "exception", "import", "class", "def",
        "repository", "commit", "branch", "pull request"
    ]

    if not any(keyword in query.lower() for keyword in engineering_keywords):
        return False, "DevSentinel handles engineering queries only"

    return True, "OK"