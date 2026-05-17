import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any


AUDIT_LOG_PATH = Path("logs/audit_log.jsonl")


def write_audit_log(event: Dict[str, Any]) -> None:
    """
    Writes one audit event to logs/audit_log.jsonl.

    Each line is a separate JSON object.
    This makes it easy to read later for audit, debugging, or reporting.
    """

    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    audit_event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **event
    }

    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(audit_event) + "\n")