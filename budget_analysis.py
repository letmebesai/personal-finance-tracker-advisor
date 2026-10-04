"""Budget calculations shared by the dashboard and advisor context."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from transaction_math import to_money


@dataclass(frozen=True)
class BudgetStatus:
    limit: Decimal
    spent: Decimal
    remaining: Decimal
    percent_used: Decimal


def evaluate_budget(limit, spent) -> BudgetStatus:
    """Calculate a budget's remaining balance and percentage consumed."""
    budget_limit = to_money(limit)
    if budget_limit <= 0:
        raise ValueError("budget limit must be positive")
    expense_total = abs(to_money(spent))
    percentage = (expense_total / budget_limit * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return BudgetStatus(budget_limit, expense_total, to_money(budget_limit - expense_total), percentage)
