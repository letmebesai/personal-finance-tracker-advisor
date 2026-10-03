import unittest
from decimal import Decimal

from goal_forecast import months_to_goal, projected_balance


class GoalForecastTests(unittest.TestCase):
    def test_projects_balance_from_monthly_savings(self):
        self.assertEqual(projected_balance("1000", "250.25", 2), Decimal("1500.50"))

    def test_rounds_goal_timeline_up_to_a_full_month(self):
        self.assertEqual(months_to_goal("100", "200", "550"), 3)

    def test_returns_none_without_positive_savings(self):
        self.assertIsNone(months_to_goal("100", "0", "550"))
