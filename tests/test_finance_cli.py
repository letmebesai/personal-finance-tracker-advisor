import unittest

from finance_cli import summarize_transactions


class FinanceCliTests(unittest.TestCase):
    def test_summarizes_imported_transactions(self):
        summary = summarize_transactions([
            {"category": "Dining", "amount": "-20"},
            {"category": "Salary", "amount": "100"},
        ])
        self.assertEqual(summary["transaction_count"], 2)
        self.assertEqual(summary["cashflow"]["net"], "80.00")
        self.assertEqual(summary["top_spending_categories"][0]["category"], "Dining")
