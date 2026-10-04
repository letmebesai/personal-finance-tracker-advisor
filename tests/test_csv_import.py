import unittest
from datetime import date
from decimal import Decimal

from csv_import import parse_transactions_csv


class CsvImportTests(unittest.TestCase):
    def test_parses_a_valid_transaction_file(self):
        rows = parse_transactions_csv("account_id,posted_date,amount,raw_description,category\na1,2026-10-03,-42.50,Coffee,Dining\n")
        self.assertEqual(rows[0]["posted_date"], date(2026, 10, 3))
        self.assertEqual(rows[0]["amount"], Decimal("-42.50"))
        self.assertEqual(rows[0]["category"], "Dining")

    def test_rejects_missing_required_columns(self):
        with self.assertRaisesRegex(ValueError, "Missing required columns"):
            parse_transactions_csv("amount\n-42.50\n")
