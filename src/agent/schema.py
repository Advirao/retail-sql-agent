"""The schema description given to the LLM — its 'first day at work' document."""

DB_SCHEMA = """
Database: retail_db (MySQL 8). All amounts are in INR.

TABLE stores (10 rows)
  store_id VARCHAR PK, store_name, city, region ('North','South','East','West'), open_date DATE

TABLE products (50 rows)
  product_id VARCHAR PK, product_name, category ('Electronics','Apparel','Grocery','Home & Kitchen','Sports'),
  unit_price DECIMAL, unit_cost DECIMAL

TABLE customers (200 rows)
  customer_id VARCHAR PK, customer_name, city, segment ('Regular','Premium','New'), join_date DATE

TABLE sales_transactions (5000 rows) -- one row per sale
  transaction_id VARCHAR PK, transaction_date DATE (2025-07-01 to 2026-06-30),
  store_id, product_id, customer_id, quantity INT, unit_price DECIMAL,
  total_amount DECIMAL, payment_method ('UPI','Card','Cash','Wallet')

TABLE `returns` (250 rows) -- one row per returned transaction
  return_id VARCHAR PK, transaction_id, return_date DATE, reason, refund_amount DECIMAL

RELATIONSHIPS (for JOINs):
  sales_transactions.store_id    -> stores.store_id
  sales_transactions.product_id  -> products.product_id
  sales_transactions.customer_id -> customers.customer_id
  `returns`.transaction_id       -> sales_transactions.transaction_id

IMPORTANT: the table name `returns` is a MySQL reserved word — ALWAYS write it in backticks.
"""