"""Pure functions used to summarize categorized spending."""

from collections import defaultdict
from collections.abc import Iterable
from decimal import Decimal

from transaction_math import to_money


def spending_by_category(transactions: Iterable[dict]) -> dict[str, Decimal]:
    """Sum debit transactions by category, excluding income and transfers."""
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    for transaction in transactions:
        amount = to_money(transaction["amount"])
        category = transaction.get("category", "Uncategorized")
        if amount < 0:
            totals[category] += -amount
    return dict(totals)


def top_spending_categories(transactions: Iterable[dict], limit: int = 3) -> list[tuple[str, Decimal]]:
    totals = spending_by_category(transactions)
    return sorted(totals.items(), key=lambda item: (-item[1], item[0]))[:limit]
