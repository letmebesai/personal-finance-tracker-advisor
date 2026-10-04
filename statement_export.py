"""CSV export for cleaned transaction data."""

import csv
from collections.abc import Iterable
from io import StringIO

from date_utils import parse_iso_date
from transaction_math import to_money


EXPORT_FIELDS = ("account_id", "posted_date", "amount", "raw_description", "category")


def transactions_to_csv(transactions: Iterable[dict]) -> str:
    """Export a normalized transaction collection with a stable column order."""
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=EXPORT_FIELDS)
    writer.writeheader()
    for transaction in transactions:
        writer.writerow({
            "account_id": transaction["account_id"],
            "posted_date": parse_iso_date(transaction["posted_date"]).isoformat(),
            "amount": str(to_money(transaction["amount"])),
            "raw_description": transaction["raw_description"],
            "category": transaction.get("category", "Uncategorized"),
        })
    return output.getvalue()
