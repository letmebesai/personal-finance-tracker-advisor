import unittest
from decimal import Decimal

from cashflow_analysis import average_monthly_net, savings_rate


class CashflowAnalysisTests(unittest.TestCase):
    def test_averages_monthly_net_cashflow(self):
        self.assertEqual(average_monthly_net([["100", "-20"], ["50", "-10"]]), Decimal("60.00"))

    def test_calculates_savings_rate(self):
        self.assertEqual(savings_rate("1000", "-250"), Decimal("75.0"))

    def test_zero_income_has_no_savings_rate(self):
        self.assertIsNone(savings_rate("0", "-250"))
