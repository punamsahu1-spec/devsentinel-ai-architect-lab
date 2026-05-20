import unittest

from app.vector_rag import retrieve_mmr_policy_chunks


class TestMMRRetrieval(unittest.TestCase):

    def test_mmr_retrieves_relevant_policy_chunks(self):
        results = retrieve_mmr_policy_chunks(
            query="hardcode passwords database connection strings pull request must be blocked rotated immediately",
            top_k=2,
            candidate_k=4,
            lambda_mult=0.7
        )

        titles = [result["title"] for result in results]

        self.assertEqual(len(results), 2)
        self.assertIn("Secret Management Policy", titles)

    def test_mmr_result_has_scores(self):
        results = retrieve_mmr_policy_chunks(
            query="prompt injection ignore previous instructions override system rules",
            top_k=2
        )

        self.assertIn("score", results[0])
        self.assertIn("title", results[0])
        self.assertIn("content", results[0])


if __name__ == "__main__":
    unittest.main()