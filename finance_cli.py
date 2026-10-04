"""Command-line entry point for statement imports and cashflow summaries."""

import argparse
import json
from pathlib import Path

from csv_import import parse_transactions_csv
from spending_insights import top_spending_categories
from transaction_math import cashflow_totals


def summarize_transactions(transactions: list[dict]) -> dict:
    """Build a JSON-safe overview of imported transactions."""
    cashflow = cashflow_totals(transaction["amount"] for transaction in transactions)
    return {
        "transaction_count": len(transactions),
        "cashflow": {key: str(value) for key, value in cashflow.items()},
        "top_spending_categories": [
            {"category": category, "spent": str(amount)}
            for category, amount in top_spending_categories(transactions)
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize a personal-finance transaction CSV.")
    parser.add_argument("statement", type=Path, help="CSV file with account_id, posted_date, amount, and raw_description columns")
    args = parser.parse_args(argv)
    transactions = parse_transactions_csv(args.statement.read_text(encoding="utf-8"))
    print(json.dumps(summarize_transactions(transactions), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
