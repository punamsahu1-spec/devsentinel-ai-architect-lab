import unittest

from app.retrieval_eval import (
    calculate_recall_at_k,
    evaluate_retrieval_at_k,
)


class TestRetrievalEval(unittest.TestCase):

    def test_calculate_recall_at_k_full_match(self):
        retrieved_titles = [
            "Secret Management Policy",
            "Pull Request Security Review Policy"
        ]
        expected_titles = ["Secret Management Policy"]

        recall = calculate_recall_at_k(
            retrieved_titles=retrieved_titles,
            expected_titles=expected_titles,
            k=2
        )

        self.assertEqual(recall, 1.0)

    def test_calculate_recall_at_k_no_match(self):
        retrieved_titles = [
            "Prompt Injection Policy",
            "Human Review Policy"
        ]
        expected_titles = ["Secret Management Policy"]

        recall = calculate_recall_at_k(
            retrieved_titles=retrieved_titles,
            expected_titles=expected_titles,
            k=2
        )

        self.assertEqual(recall, 0.0)

    def test_evaluate_retrieval_at_k_returns_results(self):
        result = evaluate_retrieval_at_k(k=2)

        self.assertIn("average_recall_at_k", result)
        self.assertIn("case_results", result)
        self.assertGreater(len(result["case_results"]), 0)


if __name__ == "__main__":
    unittest.main()