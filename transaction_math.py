"""Currency-safe arithmetic helpers for finance calculations."""

from collections.abc import Iterable
from decimal import Decimal, ROUND_HALF_UP


CENTS = Decimal("0.01")


def to_money(value: Decimal | int | float | str) -> Decimal:
    """Convert a numeric value to a two-decimal Decimal."""
    return Decimal(str(value)).quantize(CENTS, rounding=ROUND_HALF_UP)


def cashflow_totals(amounts: Iterable[Decimal | int | float | str]) -> dict[str, Decimal]:
    """Return positive income, absolute expenses, and net cashflow."""
    normalized = [to_money(amount) for amount in amounts]
    income = sum((amount for amount in normalized if amount > 0), Decimal("0.00"))
    expenses = sum((-amount for amount in normalized if amount < 0), Decimal("0.00"))
    return {"income": income, "expenses": expenses, "net": income - expenses}
