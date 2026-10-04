"""Composable transaction filtering for reports and advisor retrieval."""

from collections.abc import Iterable
from datetime import date

from date_utils import parse_iso_date


def filter_transactions(
    transactions: Iterable[dict],
    *,
    start: date | str | None = None,
    end: date | str | None = None,
    category: str | None = None,
) -> list[dict]:
    """Return transactions matching optional inclusive dates and category."""
    start_date = parse_iso_date(start) if start else None
    end_date = parse_iso_date(end) if end else None
    if start_date and end_date and start_date > end_date:
        raise ValueError("start date must not be after end date")

    matches = []
    for transaction in transactions:
        posted_date = parse_iso_date(transaction["posted_date"])
        if start_date and posted_date < start_date:
            continue
        if end_date and posted_date > end_date:
            continue
        if category and transaction.get("category") != category:
            continue
        matches.append(transaction)
    return matches
