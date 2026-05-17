from pathlib import Path
from typing import List, Dict


POLICY_PATH = Path("data/security_policy.txt")


def load_policy_text() -> str:
    """
    Loads the security policy document from data/security_policy.txt.
    """
    if not POLICY_PATH.exists():
        raise FileNotFoundError(f"Policy file not found: {POLICY_PATH}")

    return POLICY_PATH.read_text(encoding="utf-8")


def split_policy_into_sections(policy_text: str) -> List[Dict[str, str]]:
    """
    Splits the policy document into sections based on markdown headings.
    """
    sections = []
    current_title = None
    current_content = []

    for line in policy_text.splitlines():
        if line.startswith("## "):
            if current_title:
                sections.append({
                    "title": current_title,
                    "content": "\n".join(current_content).strip()
                })

            current_title = line.replace("## ", "").strip()
            current_content = []
        else:
            if current_title and line.strip():
                current_content.append(line.strip())

    if current_title:
        sections.append({
            "title": current_title,
            "content": "\n".join(current_content).strip()
        })

    return sections


def retrieve_policy_sections(query_terms: List[str], top_k: int = 2) -> List[Dict[str, str]]:
    """
    Retrieves policy sections using simple keyword matching.

    This is a beginner-friendly local retrieval method.
    """
    policy_text = load_policy_text()
    sections = split_policy_into_sections(policy_text)

    scored_sections = []

    for section in sections:
        combined_text = f"{section['title']} {section['content']}".lower()
        score = 0

        for term in query_terms:
            if term.lower() in combined_text:
                score += 1

        if score > 0:
            scored_sections.append({
                "title": section["title"],
                "content": section["content"],
                "score": score
            })

    scored_sections.sort(key=lambda item: item["score"], reverse=True)

    return scored_sections[:top_k]


def get_policy_for_findings(findings: List[Dict]) -> List[Dict[str, str]]:
    """
    Maps scan findings to policy search terms and retrieves relevant policy sections.
    """
    query_terms = []

    for finding in findings:
        finding_type = finding.get("type", "")

        if finding_type in ["password_assign", "connection_string", "aws_key", "google_api_key", "github_token", "private_key"]:
            query_terms.extend([
                "secret",
                "password",
                "api key",
                "connection string",
                "rotate",
                "blocked"
            ])

    if not query_terms:
        query_terms = ["pull request", "security review"]

    return retrieve_policy_sections(query_terms=query_terms, top_k=2)