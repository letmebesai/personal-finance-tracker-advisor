"""Detect recurring charges from normalized merchant transaction history."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class RecurringCandidate:
    merchant: str
    average_amount: float
    occurrences: int


def find_recurring_candidates(transactions: Iterable[dict], min_occurrences: int = 3) -> list[RecurringCandidate]:
    """Return merchants with repeated charges of a similar amount."""
    grouped: dict[str, list[float]] = defaultdict(list)
    for transaction in transactions:
        merchant = transaction.get("merchant_normalized", "").strip()
        try:
            amount = float(transaction.get("amount", 0))
        except (TypeError, ValueError):
            continue
        if merchant and amount < 0:
            grouped[merchant].append(abs(amount))

    candidates = []
    for merchant, amounts in grouped.items():
        if len(amounts) < min_occurrences:
            continue
        average = sum(amounts) / len(amounts)
        if max(amounts) - min(amounts) <= average * 0.1:
            candidates.append(RecurringCandidate(merchant, round(average, 2), len(amounts)))
    return sorted(candidates, key=lambda candidate: (-candidate.occurrences, candidate.merchant))
