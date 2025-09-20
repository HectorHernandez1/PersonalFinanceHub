BEGIN;

CREATE TABLE budget_app.persons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);


CREATE TABLE budget_app.spending_categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE budget_app.account_type (
    id SERIAL PRIMARY KEY,
    card_type VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE budget_app.transactions (
    id SERIAL PRIMARY KEY,
    amount DECIMAL(10,2) NOT NULL,
    merchant_name VARCHAR(1045),
    category_id INT REFERENCES budget_app.spending_categories(id) ON DELETE SET NULL,
    person_id INT REFERENCES budget_app.persons(id) ON DELETE CASCADE,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    account_type_id INT REFERENCES budget_app.account_type(id) ON DELETE SET NULL,
    CONSTRAINT unique_transaction UNIQUE (amount, merchant_name, category_id, person_id, transaction_date)
);

CREATE VIEW budget_app.transactions_view AS
SELECT 
    t.amount,
    t.merchant_name,
    s.category_name AS spending_category,
    p.name AS person,
    t.transaction_date,
    a.card_type AS account_type
FROM budget_app.transactions t
JOIN budget_app.spending_categories s ON t.category_id = s.id
JOIN budget_app.persons p ON t.person_id = p.id
JOIN budget_app.account_type a ON t.account_type_id = a.id;

-------------

INSERT INTO budget_app.spending_categories (category_name) VALUES
    ('Groceries'),
    ('Dining'),
    ('Entertainment'),
    ('Transportation'),
    ('Utilities'),
    ('Shopping'),
    ('Education'),
    ('Subscriptions'),
    ('Travel'),
    ('Personal Care'),
    ('Home Maintenance'),
    ('Other'),
    ('Refunds & Returns'),
    ('Healthcare'),
    ('Interest Charge'),
    ('Payments');


INSERT INTO budget_app.persons (name) VALUES
    ('Hector Hernandez'),
    ('Polette Rodriguez');

COMMIT;



