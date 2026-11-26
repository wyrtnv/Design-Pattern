-- GameHub: примеры SQL-запросов (только чтение, база не меняется).
-- Запуск всех сразу из папки gamehub:
--   sqlite3 -box gamehub.db < database/queries.sql

.print '1. Товары дешевле 50 000 ₸'
SELECT name, price, stock
FROM products
WHERE price < 50000
ORDER BY price;

.print '2. Три самых дорогих товара'
SELECT name, price
FROM products
ORDER BY price DESC
LIMIT 3;

.print '3. JOIN: товары категории Keyboards'
SELECT p.name, c.name AS category, p.price
FROM products p
JOIN categories c ON c.id = p.category_id
WHERE c.name = 'Keyboards';

.print '4. JOIN: заказы и покупатели'
SELECT o.id, u.full_name, o.status, o.total
FROM orders o
JOIN users u ON u.id = o.user_id;

.print '5. JOIN: позиции заказа № 1 и сумма по строке'
SELECT oi.order_id, p.name, oi.quantity, oi.unit_price,
       oi.quantity * oi.unit_price AS line_total
FROM order_items oi
JOIN products p ON p.id = oi.product_id
WHERE oi.order_id = 1;

.print '6. JOIN трёх таблиц: заказ, покупатель, платёж'
SELECT o.id, u.full_name, pay.method, pay.amount, pay.fee
FROM orders o
JOIN users u      ON u.id = o.user_id
JOIN payments pay ON pay.order_id = o.id;

.print '7. LEFT JOIN + GROUP BY: товары по категориям'
SELECT c.name AS category,
       COUNT(p.id)  AS products,
       MIN(p.price) AS min_price,
       MAX(p.price) AS max_price
FROM categories c
LEFT JOIN products p ON p.category_id = c.id
GROUP BY c.id
ORDER BY products DESC;

.print '8. CASE: наличие товара'
SELECT name, stock,
       CASE
           WHEN stock = 0  THEN 'Нет в наличии'
           WHEN stock <= 3 THEN 'Мало'
           ELSE 'Есть'
       END AS availability
FROM products
ORDER BY stock
LIMIT 4;

.print '9. CASE: размер заказа'
SELECT id, status, total,
       CASE
           WHEN total >= 150000 THEN 'Крупный'
           WHEN total >= 50000  THEN 'Средний'
           ELSE 'Мелкий'
       END AS size
FROM orders;

.print '10. Статистика для дашборда'
SELECT COUNT(*) AS orders,
       SUM(CASE WHEN status != 'CANCELLED' THEN total END) AS revenue,
       ROUND(AVG(total)) AS avg_check
FROM orders;

.print '11. GROUP BY: заказы по статусам'
SELECT status, COUNT(*) AS count
FROM orders
GROUP BY status;
