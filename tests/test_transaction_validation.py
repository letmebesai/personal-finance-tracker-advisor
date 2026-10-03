import unittest

from transaction_validation import validate_transaction


class TransactionValidationTests(unittest.TestCase):
    def test_accepts_complete_transaction(self):
        transaction = {"account_id": "a1", "posted_date": "2026-10-03", "amount": "-50", "raw_description": "Coffee"}
        self.assertEqual(validate_transaction(transaction), [])

    def test_reports_invalid_fields(self):
        errors = validate_transaction({"account_id": "", "posted_date": "03/10/2026", "amount": "zero", "raw_description": ""})
        self.assertIn("account_id is required", errors)
        self.assertIn("posted_date must use YYYY-MM-DD", errors)
        self.assertIn("amount must be numeric", errors)
