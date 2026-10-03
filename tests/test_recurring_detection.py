import unittest

from recurring_detection import find_recurring_candidates


class RecurringDetectionTests(unittest.TestCase):
    def test_detects_similarly_priced_repeated_debits(self):
        transactions = [
            {"merchant_normalized": "NETFLIX", "amount": "-649"},
            {"merchant_normalized": "NETFLIX", "amount": "-649"},
            {"merchant_normalized": "NETFLIX", "amount": "-649"},
            {"merchant_normalized": "SWIGGY", "amount": "-200"},
        ]
        candidates = find_recurring_candidates(transactions)
        self.assertEqual(candidates[0].merchant, "NETFLIX")
        self.assertEqual(candidates[0].occurrences, 3)
