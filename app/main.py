from pathlib import Path
from guardrails import scan_diff_for_secrets, validate_engineering_scope
from audit import write_audit_log
from memory_store import add_scan_event, get_recent_scan_history
from context_builder import build_context_package
from policy_retriever import get_policy_for_findings

def read_pr_diff(file_path: str) -> str:
    """
    Reads PR diff text from a local file.
    This simulates reading changed code from a pull request.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PR diff file not found: {file_path}")

    return path.read_text(encoding="utf-8")


def persist_result(result: dict) -> None:
    """
    Saves the result to audit log and memory.
    """
    write_audit_log(result)

    add_scan_event(
        source=result["source"],
        decision=result["decision"],
        reason=result["reason"],
        findings=result["findings"]
    )


def run_devsentinel(query: str, diff_text: str, source_name: str) -> dict:
    """
    Main decision function for DevSentinel.

    It checks:
    1. Is the query engineering-related?
    2. Is there any prompt injection?
    3. Are there any leaked secrets in the PR diff?
    4. Should the PR be allowed or blocked?
    5. Write audit log and memory.
    """

    scope_ok, scope_message = validate_engineering_scope(query)

    if not scope_ok:
        result = {
            "source": source_name,
            "decision": "BLOCK",
            "reason": scope_message,
            "findings": []
        }
        persist_result(result)
        return result

    secrets_found, findings = scan_diff_for_secrets(diff_text)

    if secrets_found:
        result = {
            "source": source_name,
            "decision": "BLOCK",
            "reason": "Secrets found in PR diff",
            "findings": findings
        }
        persist_result(result)
        return result

    result = {
        "source": source_name,
        "decision": "ALLOW",
        "reason": "No secrets found and query is engineering-related",
        "findings": []
    }

    persist_result(result)
    return result


def print_result(test_name: str, result: dict) -> None:
    """
    Prints the result in a readable format.
    """
    print(f"\n{test_name}")
    print("-" * len(test_name))
    print(result)


def print_recent_memory() -> None:
    """
    Prints recent scan memory.
    """
    print("\nRecent Memory")
    print("-------------")
    for event in get_recent_scan_history(limit=5):
        print({
            "source": event["source"],
            "decision": event["decision"],
            "reason": event["reason"]
        })


def print_context_package(query: str, result: dict) -> None:
    """
    Builds and prints the context package with retrieved policy context.
    """
    recent_memory = get_recent_scan_history(limit=5)
    policy_sections = get_policy_for_findings(result.get("findings", []))

    context_package = build_context_package(
        query=query,
        result=result,
        recent_memory=recent_memory,
        policy_sections=policy_sections
    )

    print("\nContext Package")
    print("---------------")
    print(context_package)

if __name__ == "__main__":
    sample_query = "Can you review this API deployment error before merge?"

    unsafe_file = "data/sample_pr_diff.txt"
    unsafe_diff = read_pr_diff(unsafe_file)
    unsafe_result = run_devsentinel(sample_query, unsafe_diff, unsafe_file)
    print_result("Unsafe PR Diff Test", unsafe_result)

    safe_file = "data/safe_pr_diff.txt"
    safe_diff = read_pr_diff(safe_file)
    safe_result = run_devsentinel(sample_query, safe_diff, safe_file)
    print_result("Safe PR Diff Test", safe_result)

    print_recent_memory()

    print_context_package(sample_query, unsafe_result)