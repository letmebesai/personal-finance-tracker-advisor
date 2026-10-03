"""Statistical outlier detection for transaction amounts."""

from collections.abc import Iterable
from statistics import mean, pstdev


def find_amount_outliers(amounts: Iterable[float], z_threshold: float = 2.0) -> list[float]:
    """Return values whose population z-score exceeds the supplied threshold."""
    values = [float(amount) for amount in amounts]
    if len(values) < 3:
        return []
    deviation = pstdev(values)
    if deviation == 0:
        return []
    average = mean(values)
    return [amount for amount in values if abs((amount - average) / deviation) >= z_threshold]
