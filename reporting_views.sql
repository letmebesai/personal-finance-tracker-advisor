-- Reporting views used by the dashboard and retrieval layer.

CREATE OR REPLACE VIEW monthly_category_spend AS
SELECT
    date_trunc('month', posted_date)::date AS month,
    category_id,
    currency,
    SUM(amount) AS net_amount,
    COUNT(*) AS transaction_count
FROM transactions
GROUP BY 1, 2, 3;

CREATE OR REPLACE VIEW transactions_needing_review AS
SELECT
    transaction_id,
    account_id,
    posted_date,
    amount,
    raw_description,
    categorization_method,
    categorization_confidence
FROM transactions
WHERE categorization_method = 'uncategorized'
   OR categorization_confidence < 0.72;
