-- ============================================================
-- Personal Finance Tracker — Core Schema (PostgreSQL)
-- ============================================================

CREATE TABLE accounts (
    account_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,              -- "HDFC Savings", "ICICI Credit Card"
    account_type    TEXT NOT NULL CHECK (account_type IN ('bank', 'credit_card', 'wallet', 'investment', 'cash')),
    institution     TEXT,                       -- "HDFC Bank", "Zerodha"
    currency        CHAR(3) NOT NULL DEFAULT 'INR',
    opening_balance NUMERIC(14,2) DEFAULT 0,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE categories (
    category_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL UNIQUE,       -- "Dining", "Rent", "Subscriptions"
    parent_id       UUID REFERENCES categories(category_id),  -- for subcategories
    category_type   TEXT NOT NULL CHECK (category_type IN ('income', 'expense', 'transfer', 'investment')),
    icon            TEXT,
    is_system       BOOLEAN DEFAULT FALSE       -- seeded defaults vs. user-created
);

CREATE TABLE transactions (
    transaction_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          UUID NOT NULL REFERENCES accounts(account_id),
    category_id         UUID REFERENCES categories(category_id),
    posted_date         DATE NOT NULL,
    amount              NUMERIC(14,2) NOT NULL,     -- negative = debit, positive = credit
    currency            CHAR(3) NOT NULL DEFAULT 'INR',
    raw_description      TEXT NOT NULL,              -- exact text from statement/CSV
    merchant_normalized  TEXT,                        -- cleaned merchant name after parsing
    categorization_method TEXT CHECK (categorization_method IN ('rule', 'ml', 'manual', 'uncategorized')),
    categorization_confidence NUMERIC(4,3),           -- 0.000–1.000, null for manual/rule
    is_recurring         BOOLEAN DEFAULT FALSE,
    notes                TEXT,
    ingested_at          TIMESTAMPTZ DEFAULT now(),
    UNIQUE (account_id, posted_date, amount, raw_description)  -- basic dedupe guard on re-import
);

CREATE INDEX idx_transactions_account_date ON transactions(account_id, posted_date);
CREATE INDEX idx_transactions_category ON transactions(category_id);
CREATE INDEX idx_transactions_merchant ON transactions(merchant_normalized);

-- Rule-based categorization rules (fast path, checked before ML fallback)
CREATE TABLE category_rules (
    rule_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id     UUID NOT NULL REFERENCES categories(category_id),
    match_type      TEXT NOT NULL CHECK (match_type IN ('exact', 'contains', 'regex')),
    pattern         TEXT NOT NULL,               -- e.g. 'SWIGGY', 'ZOMATO', '^UPI-.*NETFLIX.*$'
    priority        INT DEFAULT 100,             -- lower = checked first
    created_from    TEXT CHECK (created_from IN ('seed', 'user_correction')),
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Every time you correct a categorization, log it here.
-- This is your training signal for the ML fallback AND the source for auto-generating new rules.
CREATE TABLE category_corrections (
    correction_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id    UUID NOT NULL REFERENCES transactions(transaction_id),
    old_category_id   UUID REFERENCES categories(category_id),
    new_category_id   UUID NOT NULL REFERENCES categories(category_id),
    corrected_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE budgets (
    budget_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id     UUID NOT NULL REFERENCES categories(category_id),
    period          TEXT NOT NULL CHECK (period IN ('monthly', 'weekly', 'yearly')),
    limit_amount    NUMERIC(14,2) NOT NULL,
    effective_from  DATE NOT NULL,
    effective_to    DATE
);

CREATE TABLE recurring_rules (
    recurring_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_pattern TEXT NOT NULL,              -- matches merchant_normalized
    expected_amount  NUMERIC(14,2),
    frequency        TEXT CHECK (frequency IN ('weekly', 'monthly', 'yearly')),
    category_id      UUID REFERENCES categories(category_id),
    next_expected_date DATE,
    is_active        BOOLEAN DEFAULT TRUE
);

-- Seed a reasonable default category set
INSERT INTO categories (name, category_type, is_system) VALUES
    ('Salary', 'income', TRUE),
    ('Rent', 'expense', TRUE),
    ('Groceries', 'expense', TRUE),
    ('Dining', 'expense', TRUE),
    ('Transport', 'expense', TRUE),
    ('Utilities', 'expense', TRUE),
    ('Subscriptions', 'expense', TRUE),
    ('Healthcare', 'expense', TRUE),
    ('Shopping', 'expense', TRUE),
    ('Investments', 'investment', TRUE),
    ('Education', 'expense', TRUE),
    ('Transfer', 'transfer', TRUE),
    ('Uncategorized', 'expense', TRUE);
