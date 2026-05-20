import unittest

from app.vector_rag import retrieve_hybrid_policy_chunks, keyword_score


class TestHybridSearch(unittest.TestCase):

    def test_keyword_score_detects_overlap(self):
        score = keyword_score(
            query="DATABASE_URL API_KEY",
            text="Examples include DATABASE_URL, API_KEY, CLIENT_SECRET."
        )

        self.assertGreater(score, 0)

    def test_hybrid_retrieves_safe_configuration_policy(self):
        results = retrieve_hybrid_policy_chunks(
            query="DATABASE_URL API_KEY CLIENT_SECRET approved secret stores environment variables",
            top_k=2
        )

        titles = [result["title"] for result in results]

        self.assertIn("Safe Configuration Policy", titles)

    def test_hybrid_result_contains_vector_and_keyword_scores(self):
        results = retrieve_hybrid_policy_chunks(
            query="hardcode passwords database connection strings",
            top_k=2
        )

        self.assertIn("vector_score", results[0])
        self.assertIn("keyword_score", results[0])
        self.assertIn("score", results[0])


if __name__ == "__main__":
    unittest.main()