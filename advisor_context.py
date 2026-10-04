"""Build JSON-safe financial facts for the retrieval-grounded advisor."""

from collections.abc import Iterable

from budget_analysis import evaluate_budget
from spending_insights import top_spending_categories
from transaction_math import cashflow_totals


def build_advisor_context(transactions: Iterable[dict], budgets: Iterable[dict] = ()) -> dict:
    """Return auditable, JSON-safe facts without asking an LLM to do arithmetic."""
    transaction_list = list(transactions)
    cashflow = cashflow_totals(transaction["amount"] for transaction in transaction_list)
    budget_status = []
    for budget in budgets:
        status = evaluate_budget(budget["limit"], budget["spent"])
        budget_status.append({
            "category": budget["category"],
            "limit": str(status.limit),
            "spent": str(status.spent),
            "remaining": str(status.remaining),
            "percent_used": str(status.percent_used),
        })
    return {
        "transaction_count": len(transaction_list),
        "cashflow": {key: str(value) for key, value in cashflow.items()},
        "top_spending_categories": [
            {"category": category, "spent": str(amount)}
            for category, amount in top_spending_categories(transaction_list)
        ],
        "budgets": budget_status,
    }
