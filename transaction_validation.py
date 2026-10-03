"""Input validation before transactions are persisted."""

from datetime import date
from decimal import Decimal, InvalidOperation


REQUIRED_FIELDS = ("account_id", "posted_date", "amount", "raw_description")


def validate_transaction(transaction: dict) -> list[str]:
    """Return user-readable validation messages for one transaction."""
    errors = []
    for field in REQUIRED_FIELDS:
        if transaction.get(field) in (None, ""):
            errors.append(f"{field} is required")

    if "posted_date" in transaction and transaction.get("posted_date") not in (None, ""):
        try:
            date.fromisoformat(str(transaction["posted_date"]))
        except ValueError:
            errors.append("posted_date must use YYYY-MM-DD")

    if "amount" in transaction and transaction.get("amount") not in (None, ""):
        try:
            if Decimal(str(transaction["amount"])) == 0:
                errors.append("amount must not be zero")
        except InvalidOperation:
            errors.append("amount must be numeric")
    return errors
