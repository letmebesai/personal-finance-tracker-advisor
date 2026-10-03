import unittest
from decimal import Decimal

from transaction_math import cashflow_totals, to_money


class TransactionMathTests(unittest.TestCase):
    def test_money_rounds_to_two_decimal_places(self):
        self.assertEqual(to_money("12.345"), Decimal("12.35"))

    def test_cashflow_separates_income_and_expenses(self):
        self.assertEqual(
            cashflow_totals(["1000", "-250.50", "-49.50"]),
            {"income": Decimal("1000.00"), "expenses": Decimal("300.00"), "net": Decimal("700.00")},
        )
