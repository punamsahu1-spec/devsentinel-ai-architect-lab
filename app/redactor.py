import re
from typing import Dict


REDACTION_PATTERNS: Dict[str, str] = {
    "aws_key": r"AKIA[0-9A-Z]{16}",
    "google_api_key": r"AIza[0-9A-Za-z\-_]{35}",
    "github_token": r"ghp_[0-9a-zA-Z]{36}",
    "private_key": r"-----BEGIN (RSA |EC )?PRIVATE KEY-----.*?-----END (RSA |EC )?PRIVATE KEY-----",
    "password_assign": r"(password|passwd|pwd|secret|api_key)\s*=\s*['\"][^'\"]{8,}['\"]",
    "connection_string": r"(mongodb|postgresql|mysql):\/\/[^:]+:[^@]+@[^'\"\s]+",
}


def redact_secrets(text: str) -> str:
    """
    Redacts secret values from text before sending content to logs, memory, or LLM.
    """

    redacted_text = text

    for secret_type, pattern in REDACTION_PATTERNS.items():
        redacted_text = re.sub(
            pattern,
            f"[REDACTED_{secret_type.upper()}]",
            redacted_text,
            flags=re.IGNORECASE | re.DOTALL,
        )

    return redacted_text