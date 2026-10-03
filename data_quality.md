# Data Quality Guide

Reliable advice begins with reliable transaction data. Validate imported rows
before persisting them, preserve the original bank description, and store a
normalized merchant key separately for grouping.

## Import checks

- Require an account identifier, ISO posted date, non-zero amount, and raw description.
- Reject malformed rows instead of silently substituting values.
- Keep imports idempotent through the transaction uniqueness constraint.

## Categorization checks

- Prefer deterministic rules when a known merchant is present.
- Keep low-confidence results in the review queue.
- Promote a correction into a rule only after repeated confirmation.

## Advisor checks

- Build advisor context from reporting views rather than raw arithmetic in prompts.
- Retain query context and the response for later review.
