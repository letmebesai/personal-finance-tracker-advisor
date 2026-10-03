import unittest
from decimal import Decimal

from spending_insights import top_spending_categories


class SpendingInsightTests(unittest.TestCase):
    def test_returns_largest_categories_first(self):
        transactions = [
            {"category": "Dining", "amount": "-200"},
            {"category": "Groceries", "amount": "-500"},
            {"category": "Salary", "amount": "2000"},
        ]
        self.assertEqual(
            top_spending_categories(transactions),
            [("Groceries", Decimal("500.00")), ("Dining", Decimal("200.00"))],
        )
