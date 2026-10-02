"""Small, deterministic helpers for grouping merchant descriptions."""

import re


NOISE_TOKENS = {"UPI", "POS", "CARD", "DEBIT", "CREDIT", "PAYMENT", "TXN"}


def normalize_merchant(description: str) -> str:
    """Return a stable merchant key from a bank transaction description."""
    upper = description.upper().strip()
    cleaned = re.sub(r"[^A-Z0-9 ]+", " ", upper)
    tokens = [token for token in cleaned.split() if token not in NOISE_TOKENS]
    return " ".join(tokens)
