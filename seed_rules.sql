-- Starter rules for common Indian transaction descriptions.
-- Re-running this file does not duplicate an existing category/pattern pair.

WITH starter_rules(category_name, match_type, pattern, priority) AS (
    VALUES
        ('Dining', 'contains', 'SWIGGY', 20),
        ('Dining', 'contains', 'ZOMATO', 20),
        ('Groceries', 'contains', 'DMART', 20),
        ('Transport', 'contains', 'UBER', 20),
        ('Transport', 'contains', 'OLA', 20),
        ('Subscriptions', 'contains', 'NETFLIX', 20),
        ('Subscriptions', 'contains', 'SPOTIFY', 20)
)
INSERT INTO category_rules (category_id, match_type, pattern, priority, created_from)
SELECT c.category_id, s.match_type, s.pattern, s.priority, 'seed'
FROM starter_rules AS s
JOIN categories AS c ON c.name = s.category_name
WHERE NOT EXISTS (
    SELECT 1
    FROM category_rules AS existing
    WHERE existing.category_id = c.category_id
      AND existing.pattern = s.pattern
);
