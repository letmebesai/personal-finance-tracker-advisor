import unittest

from transaction_filters import filter_transactions


class TransactionFilterTests(unittest.TestCase):
    def test_filters_by_date_and_category(self):
        transactions = [
            {"posted_date": "2026-01-02", "category": "Dining"},
            {"posted_date": "2026-01-10", "category": "Groceries"},
            {"posted_date": "2026-02-01", "category": "Dining"},
        ]
        result = filter_transactions(transactions, start="2026-01-01", end="2026-01-31", category="Dining")
        self.assertEqual(result, [transactions[0]])

    def test_rejects_inverted_date_range(self):
        with self.assertRaises(ValueError):
            filter_transactions([], start="2026-02-01", end="2026-01-01")
