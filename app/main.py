from guardrails import scan_diff_for_secrets, validate_engineering_scope


def run_devsentinel(query: str, diff_text: str) -> dict:
    """
    Main decision function for DevSentinel.

    It checks:
    1. Is the query engineering-related?
    2. Is there any prompt injection?
    3. Are there any leaked secrets in the PR diff?
    4. Should the PR be allowed or blocked?
    """

    scope_ok, scope_message = validate_engineering_scope(query)

    if not scope_ok:
        return {
            "decision": "BLOCK",
            "reason": scope_message,
            "findings": []
        }

    secrets_found, findings = scan_diff_for_secrets(diff_text)

    if secrets_found:
        return {
            "decision": "BLOCK",
            "reason": "Secrets found in PR diff",
            "findings": findings
        }

    return {
        "decision": "ALLOW",
        "reason": "No secrets found and query is engineering-related",
        "findings": []
    }


if __name__ == "__main__":
    sample_query = "Can you review this API deployment error before merge?"

    sample_diff = """
    + password = "mysecretpassword123"
    + database_url = "postgresql://admin:adminpass@localhost:5432/appdb"
    """

    result = run_devsentinel(sample_query, sample_diff)

    print("\nDevSentinel Result")
    print("------------------")
    print(result)