-- Current-month category budget progress for the dashboard and advisor context.

CREATE OR REPLACE VIEW current_budget_status AS
SELECT
    b.budget_id,
    c.name AS category_name,
    b.limit_amount,
    COALESCE(SUM(ABS(t.amount)) FILTER (WHERE t.amount < 0), 0) AS spent_amount,
    b.limit_amount - COALESCE(SUM(ABS(t.amount)) FILTER (WHERE t.amount < 0), 0) AS remaining_amount
FROM budgets AS b
JOIN categories AS c ON c.category_id = b.category_id
LEFT JOIN transactions AS t
    ON t.category_id = b.category_id
   AND date_trunc('month', t.posted_date) = date_trunc('month', CURRENT_DATE)
WHERE b.period = 'monthly'
  AND b.effective_from <= CURRENT_DATE
  AND (b.effective_to IS NULL OR b.effective_to >= CURRENT_DATE)
GROUP BY b.budget_id, c.name, b.limit_amount;
