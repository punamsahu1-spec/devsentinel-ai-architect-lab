from typing import List, Dict, Any

try:
    from .vector_rag import retrieve_top_k_policy_chunks
except ImportError:
    from vector_rag import retrieve_top_k_policy_chunks


GOLDEN_RETRIEVAL_CASES = [
    {
        "name": "hardcoded_password_secret",
        "query": "hardcode passwords database connection strings rotated immediately pull request must be blocked",
        "expected_titles": ["Secret Management Policy"]
    },
    {
        "name": "pull_request_secret_scan",
        "query": "pull request leaked secrets merge must be blocked rerun scan before approval",
        "expected_titles": ["Pull Request Security Review Policy"]
    },
    {
        "name": "prompt_injection",
        "query": "ignore previous instructions bypass controls override security policy",
        "expected_titles": ["Prompt Injection Policy"]
    },
    {
        "name": "safe_configuration",
        "query": "environment variables approved secret stores DATABASE_URL API_KEY CLIENT_SECRET",
        "expected_titles": ["Safe Configuration Policy"]
    },
    {
        "name": "human_review",
        "query": "uncertain risk repeated secret exposure production credentials human review required",
        "expected_titles": ["Human Review Policy"]
    }
]


def calculate_recall_at_k(
    retrieved_titles: List[str],
    expected_titles: List[str],
    k: int
) -> float:
    """
    Calculates Recall@K.

    Recall@K = number of expected titles found in top-k / total expected titles.
    """
    top_k_titles = retrieved_titles[:k]

    matched = [
        title for title in expected_titles
        if title in top_k_titles
    ]

    if not expected_titles:
        return 0.0

    return len(matched) / len(expected_titles)


def evaluate_retrieval_at_k(k: int = 2) -> Dict[str, Any]:
    """
    Evaluates vector retrieval using golden test cases.
    """
    case_results = []
    recall_scores = []

    for case in GOLDEN_RETRIEVAL_CASES:
        retrieved_chunks = retrieve_top_k_policy_chunks(
            query=case["query"],
            top_k=k
        )

        retrieved_titles = [
            chunk["title"] for chunk in retrieved_chunks
        ]

        recall = calculate_recall_at_k(
            retrieved_titles=retrieved_titles,
            expected_titles=case["expected_titles"],
            k=k
        )

        recall_scores.append(recall)

        case_results.append({
            "name": case["name"],
            "query": case["query"],
            "expected_titles": case["expected_titles"],
            "retrieved_titles": retrieved_titles,
            "recall_at_k": recall
        })

    average_recall = sum(recall_scores) / len(recall_scores)

    return {
        "k": k,
        "average_recall_at_k": round(average_recall, 4),
        "case_results": case_results
    }


if __name__ == "__main__":
    result = evaluate_retrieval_at_k(k=2)

    print("Retrieval Evaluation")
    print("--------------------")
    print(result)