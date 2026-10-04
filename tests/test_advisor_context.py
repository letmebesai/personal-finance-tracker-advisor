import unittest

from advisor_context import build_advisor_context


class AdvisorContextTests(unittest.TestCase):
    def test_builds_json_safe_financial_facts(self):
        context = build_advisor_context(
            [{"category": "Dining", "amount": "-50"}, {"category": "Salary", "amount": "500"}],
            [{"category": "Dining", "limit": "200", "spent": "-50"}],
        )
        self.assertEqual(context["cashflow"]["net"], "450.00")
        self.assertEqual(context["top_spending_categories"][0]["category"], "Dining")
        self.assertEqual(context["budgets"][0]["remaining"], "150.00")
