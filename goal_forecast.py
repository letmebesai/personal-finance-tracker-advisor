"""Simple, explainable goal forecasting helpers."""

from decimal import Decimal, ROUND_CEILING

from transaction_math import to_money


def projected_balance(current_balance, monthly_savings, months: int) -> Decimal:
    if months < 0:
        raise ValueError("months must not be negative")
    return to_money(to_money(current_balance) + to_money(monthly_savings) * months)


def months_to_goal(current_balance, monthly_savings, goal_amount) -> int | None:
    """Return months needed for a target, or None when savings are not positive."""
    current = to_money(current_balance)
    goal = to_money(goal_amount)
    savings = to_money(monthly_savings)
    if current >= goal:
        return 0
    if savings <= 0:
        return None
    return int(((goal - current) / savings).to_integral_value(rounding=ROUND_CEILING))
