import unittest
from decimal import Decimal

from budget_analysis import evaluate_budget


class BudgetAnalysisTests(unittest.TestCase):
    def test_calculates_remaining_amount_and_percentage(self):
        status = evaluate_budget("1000", "-250.50")
        self.assertEqual(status.remaining, Decimal("749.50"))
        self.assertEqual(status.percent_used, Decimal("25.1"))

    def test_rejects_non_positive_budget_limit(self):
        with self.assertRaises(ValueError):
            evaluate_budget("0", "10")
