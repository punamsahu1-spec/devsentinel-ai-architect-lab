import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any, Tuple


POLICY_PATH = Path("data/security_policy.txt")
VECTOR_INDEX_PATH = Path("data/policy_vector_index.json")


def tokenize(text: str) -> List[str]:
    """
    Converts text into lowercase tokens.
    This is a simple local tokenizer for free-tier vector retrieval.
    """
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


def chunk_policy_by_headings(policy_text: str) -> List[Dict[str, Any]]:
    """
    Splits policy text into chunks using markdown headings.
    Each section becomes one chunk.
    """
    chunks = []
    current_title = None
    current_content = []

    for line in policy_text.splitlines():
        if line.startswith("## "):
            if current_title:
                chunks.append({
                    "chunk_id": f"policy_chunk_{len(chunks) + 1}",
                    "title": current_title,
                    "content": "\n".join(current_content).strip()
                })

            current_title = line.replace("## ", "").strip()
            current_content = []
        else:
            if current_title and line.strip():
                current_content.append(line.strip())

    if current_title:
        chunks.append({
            "chunk_id": f"policy_chunk_{len(chunks) + 1}",
            "title": current_title,
            "content": "\n".join(current_content).strip()
        })

    return chunks


def build_vocabulary(texts: List[str]) -> List[str]:
    """
    Builds a sorted vocabulary from all chunks.
    """
    vocab = set()

    for text in texts:
        vocab.update(tokenize(text))

    return sorted(vocab)


def embed_text(text: str, vocabulary: List[str]) -> List[float]:
    """
    Converts text into a simple term-frequency vector.
    This is a lightweight local embedding.
    """
    tokens = tokenize(text)
    counts = Counter(tokens)
    total_tokens = len(tokens) or 1

    return [
        counts.get(term, 0) / total_tokens
        for term in vocabulary
    ]


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Calculates cosine similarity between two vectors.
    """
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def build_policy_vector_index() -> Dict[str, Any]:
    """
    Builds a local vector index from security_policy.txt.
    """
    if not POLICY_PATH.exists():
        raise FileNotFoundError(f"Policy file not found: {POLICY_PATH}")

    policy_text = POLICY_PATH.read_text(encoding="utf-8")
    chunks = chunk_policy_by_headings(policy_text)

    chunk_texts = [
        f"{chunk['title']} {chunk['content']}"
        for chunk in chunks
    ]

    vocabulary = build_vocabulary(chunk_texts)

    indexed_chunks = []

    for chunk in chunks:
        text_for_embedding = f"{chunk['title']} {chunk['content']}"
        vector = embed_text(text_for_embedding, vocabulary)

        indexed_chunks.append({
            "chunk_id": chunk["chunk_id"],
            "title": chunk["title"],
            "content": chunk["content"],
            "embedding": vector
        })

    index = {
        "index_type": "local_term_frequency_vector_index",
        "embedding_method": "term_frequency",
        "vocabulary": vocabulary,
        "chunks": indexed_chunks
    }

    VECTOR_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    VECTOR_INDEX_PATH.write_text(json.dumps(index, indent=2), encoding="utf-8")

    return index


def load_policy_vector_index() -> Dict[str, Any]:
    """
    Loads vector index. Builds it if missing.
    """
    if not VECTOR_INDEX_PATH.exists():
        return build_policy_vector_index()

    return json.loads(VECTOR_INDEX_PATH.read_text(encoding="utf-8"))


def retrieve_top_k_policy_chunks(query: str, top_k: int = 2) -> List[Dict[str, Any]]:
    """
    Retrieves top-k most similar policy chunks for a query.
    """
    index = load_policy_vector_index()

    vocabulary = index["vocabulary"]
    query_vector = embed_text(query, vocabulary)

    scored_chunks = []

    for chunk in index["chunks"]:
        score = cosine_similarity(query_vector, chunk["embedding"])

        scored_chunks.append({
            "chunk_id": chunk["chunk_id"],
            "title": chunk["title"],
            "content": chunk["content"],
            "score": round(score, 4)
        })

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)

    return scored_chunks[:top_k]
def retrieve_mmr_policy_chunks(
    query: str,
    top_k: int = 2,
    candidate_k: int = 4,
    lambda_mult: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Retrieves policy chunks using Maximal Marginal Relevance.

    MMR balances:
    - relevance to the query
    - diversity from already selected chunks

    lambda_mult closer to 1.0 = prioritize relevance
    lambda_mult closer to 0.0 = prioritize diversity
    """
    index = load_policy_vector_index()

    vocabulary = index["vocabulary"]
    query_vector = embed_text(query, vocabulary)

    candidates = []

    for chunk in index["chunks"]:
        chunk_vector = chunk["embedding"]
        relevance_score = cosine_similarity(query_vector, chunk_vector)

        candidates.append({
            "chunk_id": chunk["chunk_id"],
            "title": chunk["title"],
            "content": chunk["content"],
            "embedding": chunk_vector,
            "score": relevance_score
        })

    candidates.sort(key=lambda item: item["score"], reverse=True)
    candidates = candidates[:candidate_k]

    selected = []

    while candidates and len(selected) < top_k:
        if not selected:
            selected.append(candidates.pop(0))
            continue

        best_candidate = None
        best_mmr_score = float("-inf")

        for candidate in candidates:
            max_similarity_to_selected = max(
                cosine_similarity(candidate["embedding"], selected_chunk["embedding"])
                for selected_chunk in selected
            )

            mmr_score = (
                lambda_mult * candidate["score"]
                - (1 - lambda_mult) * max_similarity_to_selected
            )

            if mmr_score > best_mmr_score:
                best_mmr_score = mmr_score
                best_candidate = candidate

        selected.append(best_candidate)
        candidates.remove(best_candidate)

    return [
        {
            "chunk_id": chunk["chunk_id"],
            "title": chunk["title"],
            "content": chunk["content"],
            "score": round(chunk["score"], 4)
        }
        for chunk in selected
    ]
def keyword_score(query: str, text: str) -> float:
    """
    Calculates a simple keyword overlap score.
    """
    query_tokens = set(tokenize(query))
    text_tokens = set(tokenize(text))

    if not query_tokens:
        return 0.0

    overlap = query_tokens.intersection(text_tokens)

    return len(overlap) / len(query_tokens)


def retrieve_hybrid_policy_chunks(
    query: str,
    top_k: int = 2,
    vector_weight: float = 0.7,
    keyword_weight: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Retrieves policy chunks using hybrid search.

    Hybrid score = vector similarity score + keyword overlap score.
    """
    index = load_policy_vector_index()

    vocabulary = index["vocabulary"]
    query_vector = embed_text(query, vocabulary)

    scored_chunks = []

    for chunk in index["chunks"]:
        chunk_text = f"{chunk['title']} {chunk['content']}"

        vector_score = cosine_similarity(query_vector, chunk["embedding"])
        lexical_score = keyword_score(query, chunk_text)

        hybrid_score = (
            vector_weight * vector_score
            + keyword_weight * lexical_score
        )

        scored_chunks.append({
            "chunk_id": chunk["chunk_id"],
            "title": chunk["title"],
            "content": chunk["content"],
            "vector_score": round(vector_score, 4),
            "keyword_score": round(lexical_score, 4),
            "score": round(hybrid_score, 4)
        })

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)

    return scored_chunks[:top_k]
if __name__ == "__main__":
    build_policy_vector_index()

    results = retrieve_top_k_policy_chunks(
        query="hardcoded password database connection string secret rotation",
        top_k=2
    )

    print(json.dumps(results, indent=2))