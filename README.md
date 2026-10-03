# Personal Finance Tracker Advisor

A PostgreSQL-backed personal finance tracker with an explainable transaction
categorization pipeline and a retrieval-grounded financial analysis assistant.

## What it does

- Stores accounts, transactions, categories, budgets, and recurring payments.
- Categorizes transactions through rules first, then embedding similarity.
- Learns candidate rules from repeated manual corrections.
- Grounds advisor responses in computed financial data instead of invented figures.

## Project layout

| File | Purpose |
| --- | --- |
| `schema.sql` | Core PostgreSQL tables, indexes, and default categories. |
| `categorization_pipeline.py` | Rules, embedding fallback, ingestion, and feedback loop. |
| `rag_advisor_design.md` | Retrieval design and safety guardrails for the advisor. |
| `reporting_views.sql` | Dashboard-ready category rollups and review queue. |
| `seed_rules.sql` | Idempotent starter rules for common merchants. |
| `budget_queries.sql` | Current-month budget progress view. |
| `recurring_detection.py` | Repeated-charge candidate detector. |
| `cashflow_queries.sql` | Monthly income, expense, and net cashflow view. |

## Quick start

1. Create a PostgreSQL database with the `pgcrypto` extension enabled.
2. Run `psql -d finance_tracker -f schema.sql` followed by `psql -d finance_tracker -f reporting_views.sql`.
3. Install the Python dependencies with `pip install -r requirements.txt`.
4. Configure your database connection and call `ingest_and_categorize` with new transactions.

## Quality checks

Run `python -m unittest discover -s tests` before opening a change. GitHub Actions runs the same test command on pushes and pull requests.

See `data_quality.md` for the import and categorization checks that keep advisor responses grounded.

## Scope

The advisor is intended for spending analysis and pattern detection. It does not
provide investment, tax, or legal advice.
