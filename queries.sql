-- 1. Number of clients in each district
SELECT d.A2 AS district_name, COUNT(c.client_id) AS total_clients
FROM client c
JOIN district d ON c.district_id = d.district_id
GROUP BY d.A2
ORDER BY total_clients DESC;

-- 2. Average loan amount by district
SELECT d.A2 AS district_name, AVG(l.amount) AS avg_loan
FROM loan l
JOIN account a ON l.account_id = a.account_id
JOIN district d ON a.district_id = d.district_id
GROUP BY d.A2
ORDER BY avg_loan DESC;

-- 3. Minimum and maximum loan amount
SELECT MIN(amount) AS min_loan, MAX(amount) AS max_loan
FROM loan;

--4. Number of accounts by opening year
SELECT EXTRACT(YEAR FROM a.date) AS year_opened, COUNT(a.account_id) AS total_accounts
FROM account a
GROUP BY year_opened
ORDER BY year_opened;

-- 5. Number of clients with different card types
SELECT c2.type AS card_type, COUNT(c2.card_id) AS total_cards
FROM card c2
GROUP BY c2.type
ORDER BY total_cards DESC;

-- 6. Number of transactions by type (e.g., credit, debit)
SELECT t.type, COUNT(t.trans_id) AS total_trans
FROM trans t
GROUP BY t.type
ORDER BY total_trans DESC;

-- 7. Average transaction amount by type
SELECT t.type, AVG(t.amount) AS avg_amount
FROM trans t
GROUP BY t.type
ORDER BY avg_amount DESC;

-- 8. Number of loans by status (e.g., paid off, overdue)
SELECT l.status, COUNT(l.loan_id) AS total_loans
FROM loan l
GROUP BY l.status
ORDER BY total_loans DESC;

-- 9. Top 5 clients by number of accounts
SELECT c.client_id, COUNT(a.account_id) AS accounts_count
FROM client c
JOIN disp d ON c.client_id = d.client_id
JOIN account a ON d.account_id = a.account_id
GROUP BY c.client_id
ORDER BY accounts_count DESC
LIMIT 5;

-- 10. Total transaction amount for each account (TOP 10)
SELECT a.account_id, SUM(t.amount) AS total_amount
FROM account a
JOIN trans t ON a.account_id = t.account_id
GROUP BY a.account_id
ORDER BY total_amount DESC
LIMIT 10;
