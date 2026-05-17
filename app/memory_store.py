import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List


MEMORY_PATH = Path("data/memory.json")


DEFAULT_MEMORY = {
    "scan_history": [],
    "known_risks": [],
    "team_patterns": []
}


def get_default_memory() -> Dict[str, Any]:
    """
    Returns a fresh default memory object.
    """
    return {
        "scan_history": [],
        "known_risks": [],
        "team_patterns": []
    }


def load_memory() -> Dict[str, Any]:
    """
    Loads memory from data/memory.json.

    If the file is missing or corrupted, it resets memory safely.
    """
    if not MEMORY_PATH.exists():
        memory = get_default_memory()
        save_memory(memory)
        return memory

    try:
        with MEMORY_PATH.open("r", encoding="utf-8") as file:
            memory = json.load(file)

        if not isinstance(memory, dict):
            memory = get_default_memory()
            save_memory(memory)

        memory.setdefault("scan_history", [])
        memory.setdefault("known_risks", [])
        memory.setdefault("team_patterns", [])

        return memory

    except json.JSONDecodeError:
        memory = get_default_memory()
        save_memory(memory)
        return memory


def save_memory(memory: Dict[str, Any]) -> None:
    """
    Saves memory back to data/memory.json.
    """
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)

    with MEMORY_PATH.open("w", encoding="utf-8") as file:
        json.dump(memory, file, indent=2)


def add_scan_event(source: str, decision: str, reason: str, findings: List[Dict[str, Any]]) -> None:
    """
    Adds one scan event to long-term memory.
    """
    memory = load_memory()

    event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "decision": decision,
        "reason": reason,
        "findings": findings
    }

    memory["scan_history"].append(event)

    if decision == "BLOCK":
        memory["known_risks"].append({
            "timestamp_utc": event["timestamp_utc"],
            "source": source,
            "reason": reason,
            "finding_types": [finding["type"] for finding in findings]
        })

    save_memory(memory)


def get_recent_scan_history(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Returns the most recent scan events.
    """
    memory = load_memory()
    return memory.get("scan_history", [])[-limit:]