import unittest

from app.reranker import rerank_policy_chunks


class TestReranker(unittest.TestCase):

    def test_reranker_prioritizes_pull_request_policy(self):
        query = "hardcoded password secret exposed pull request merge blocked credential rotation"

        chunks = [
            {
                "title": "Human Review Policy",
                "content": "Human review is required for repeated secret exposure or production credentials.",
                "score": 0.29
            },
            {
                "title": "Pull Request Security Review Policy",
                "content": "Every pull request must be scanned for leaked secrets before merge. If critical secrets are found, the merge must be blocked.",
                "score": 0.28
            },
            {
                "title": "Secret Management Policy",
                "content": "Developers must never hardcode passwords or database connection strings in source code.",
                "score": 0.40
            }
        ]

        reranked = rerank_policy_chunks(query=query, chunks=chunks, top_k=2)

        titles = [chunk["title"] for chunk in reranked]

        self.assertIn("Secret Management Policy", titles)
        self.assertIn("Pull Request Security Review Policy", titles)

    def test_reranker_adds_rerank_score(self):
        query = "pull request merge blocked secret"

        chunks = [
            {
                "title": "Pull Request Security Review Policy",
                "content": "The merge must be blocked if critical secrets are found.",
                "score": 0.30
            }
        ]

        reranked = rerank_policy_chunks(query=query, chunks=chunks, top_k=1)

        self.assertIn("original_score", reranked[0])
        self.assertIn("rerank_score", reranked[0])
        self.assertGreaterEqual(
            reranked[0]["rerank_score"],
            reranked[0]["original_score"]
        )


if __name__ == "__main__":
    unittest.main()