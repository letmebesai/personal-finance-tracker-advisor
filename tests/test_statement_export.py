import unittest

from statement_export import transactions_to_csv


class StatementExportTests(unittest.TestCase):
    def test_exports_stable_headers_and_money_format(self):
        csv_text = transactions_to_csv([
            {"account_id": "a1", "posted_date": "2026-10-04", "amount": "-25", "raw_description": "Lunch", "category": "Dining"}
        ])
        self.assertIn("account_id,posted_date,amount,raw_description,category", csv_text)
        self.assertIn("a1,2026-10-04,-25.00,Lunch,Dining", csv_text)
