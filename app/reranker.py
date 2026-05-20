from typing import List, Dict, Any


def rerank_policy_chunks(
    query: str,
    chunks: List[Dict[str, Any]],
    top_k: int = 2
) -> List[Dict[str, Any]]:
    """
    Reranks retrieved policy chunks using domain-specific relevance signals.

    This is a lightweight local reranker.
    Later, this can be replaced with a cross-encoder reranker.
    """

    query_lower = query.lower()

    priority_terms = [
        "pull request",
        "merge",
        "blocked",
        "block",
        "secret",
        "secrets",
        "hardcode",
        "hardcoded",
        "password",
        "database connection",
        "credential",
        "rotation",
        "rotate",
    ]

    reranked = []

    for chunk in chunks:
        title = chunk.get("title", "")
        content = chunk.get("content", "")
        combined_text = f"{title} {content}".lower()

        original_score = float(chunk.get("score", 0))

        term_boost = 0

        for term in priority_terms:
            if term in query_lower and term in combined_text:
                term_boost += 0.05

        # Directly boost PR security review when the query is PR/merge/block related.
        if "pull request" in query_lower and "pull request" in combined_text:
            term_boost += 0.15

        if "merge" in query_lower and "merge" in combined_text:
            term_boost += 0.10

        if "blocked" in query_lower and "blocked" in combined_text:
            term_boost += 0.10

        rerank_score = original_score + term_boost

        updated_chunk = {
            **chunk,
            "original_score": round(original_score, 4),
            "rerank_score": round(rerank_score, 4),
        }

        reranked.append(updated_chunk)

    reranked.sort(key=lambda item: item["rerank_score"], reverse=True)

    return reranked[:top_k]