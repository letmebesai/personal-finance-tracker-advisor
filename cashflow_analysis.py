"""Monthly cashflow and savings-rate calculations."""

from collections.abc import Iterable
from decimal import Decimal, ROUND_HALF_UP

from transaction_math import cashflow_totals, to_money


def average_monthly_net(months: Iterable[Iterable]) -> Decimal:
    """Return the average net amount across non-empty monthly amount groups."""
    monthly_nets = [cashflow_totals(amounts)["net"] for amounts in months]
    if not monthly_nets:
        return Decimal("0.00")
    return to_money(sum(monthly_nets, Decimal("0.00")) / len(monthly_nets))


def savings_rate(income, expenses) -> Decimal | None:
    """Return savings as a percentage of income, or None when income is zero."""
    income_amount = to_money(income)
    if income_amount <= 0:
        return None
    expense_amount = abs(to_money(expenses))
    return ((income_amount - expense_amount) / income_amount * 100).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP
    )
