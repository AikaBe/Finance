-- name: pie_gender
-- type: pie
-- title: Распределение клиентов по полу
-- xlabel: 
-- ylabel: Количество клиентов
SELECT c.gender, COUNT(*) AS cnt
FROM client c
INNER JOIN disp d ON c.client_id = d.client_id
INNER JOIN account a ON d.account_id = a.account_id
GROUP BY c.gender;

-- name: bar_loans
-- type: bar
-- title: Количество кредитов по статусу
-- xlabel: Статус кредита
-- ylabel: Количество
SELECT l.status, COUNT(a.account_id) AS cnt
FROM loan l
LEFT JOIN account a ON l.account_id = a.account_id
GROUP BY l.status;

-- name: barh_operations
-- type: barh
-- title: Средняя сумма транзакций по операциям
-- xlabel: Средняя сумма
-- ylabel: Операция
SELECT t.operation, AVG(t.amount) AS avg_amount
FROM account a
LEFT JOIN trans t ON a.account_id = t.account_id
GROUP BY t.operation;

-- name: line_monthly
-- type: line
-- title: Сумма транзакций по месяцам
-- xlabel: Месяц
-- ylabel: Сумма
SELECT TO_CHAR(t.date, 'YYYY-MM') AS month, SUM(t.amount) AS total_amount
FROM trans t
GROUP BY TO_CHAR(t.date, 'YYYY-MM')
ORDER BY month;

-- name: hist_age
-- type: hist
-- title: Распределение клиентов по возрасту
-- xlabel: Возраст
-- ylabel: Количество
SELECT EXTRACT(YEAR FROM AGE(c.birth_date)) AS age
FROM client c
LEFT JOIN disp d ON c.client_id = d.client_id
LEFT JOIN account a ON d.account_id = a.account_id
WHERE c.birth_date IS NOT NULL;

-- name: scatter_loans
-- type: scatter
-- title: Кредиты: сумма против длительности
-- xlabel: Длительность
-- ylabel: Сумма
SELECT l.duration, l.amount
FROM loan l
INNER JOIN account a ON l.account_id = a.account_id
WHERE l.duration IS NOT NULL AND l.amount IS NOT NULL;
