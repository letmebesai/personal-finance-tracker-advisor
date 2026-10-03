-- Monthly cashflow facts for forecasting and grounded advisor responses.

CREATE OR REPLACE VIEW monthly_cashflow AS
SELECT
    date_trunc('month', posted_date)::date AS month,
    currency,
    COALESCE(SUM(amount) FILTER (WHERE amount > 0), 0) AS income_amount,
    COALESCE(ABS(SUM(amount) FILTER (WHERE amount < 0)), 0) AS expense_amount,
    SUM(amount) AS net_cashflow
FROM transactions
GROUP BY 1, 2;
