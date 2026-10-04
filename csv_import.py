"""CSV parsing helpers for bank statement imports."""

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from io import StringIO


REQUIRED_COLUMNS = {"account_id", "posted_date", "amount", "raw_description"}


def parse_transactions_csv(contents: str) -> list[dict]:
    """Parse a standard transaction CSV and reject malformed rows early."""
    reader = csv.DictReader(StringIO(contents))
    fieldnames = set(reader.fieldnames or [])
    missing = REQUIRED_COLUMNS - fieldnames
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    transactions = []
    for row_number, row in enumerate(reader, start=2):
        account_id = (row["account_id"] or "").strip()
        raw_description = (row["raw_description"] or "").strip()
        try:
            posted_date = date.fromisoformat(row["posted_date"])
            amount = Decimal(row["amount"])
        except (TypeError, ValueError, InvalidOperation) as error:
            raise ValueError(f"Invalid transaction at row {row_number}") from error
        if not account_id or not raw_description or amount == 0:
            raise ValueError(f"Incomplete transaction at row {row_number}")
        transaction = {
            "account_id": account_id,
            "posted_date": posted_date,
            "amount": amount,
            "raw_description": raw_description,
        }
        category = (row.get("category") or "").strip()
        if category:
            transaction["category"] = category
        transactions.append(transaction)
    return transactions
