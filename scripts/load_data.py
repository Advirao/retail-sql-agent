"""
Load the 5 retail CSVs into MySQL.
Idempotent: drops and recreates tables on every run.
Usage:  uv run scripts/load_data.py
"""

import os
from pathlib import Path

import pandas as pd
import mysql.connector
from dotenv import load_dotenv

load_dotenv()  # pulls MYSQL_* variables from .env into the environment

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# ---- 1. Schema: table name -> CREATE TABLE statement ----
SCHEMAS = {
    "stores": """
        CREATE TABLE stores (
            store_id    VARCHAR(10) PRIMARY KEY,
            store_name  VARCHAR(100),
            city        VARCHAR(50),
            region      VARCHAR(20),
            open_date   DATE
        )""",
    "products": """
        CREATE TABLE products (
            product_id   VARCHAR(10) PRIMARY KEY,
            product_name VARCHAR(100),
            category     VARCHAR(50),
            unit_price   DECIMAL(10,2),
            unit_cost    DECIMAL(10,2)
        )""",
    "customers": """
        CREATE TABLE customers (
            customer_id   VARCHAR(10) PRIMARY KEY,
            customer_name VARCHAR(100),
            city          VARCHAR(50),
            segment       VARCHAR(20),
            join_date     DATE
        )""",
    "sales_transactions": """
        CREATE TABLE sales_transactions (
            transaction_id   VARCHAR(12) PRIMARY KEY,
            transaction_date DATE,
            store_id         VARCHAR(10),
            product_id       VARCHAR(10),
            customer_id      VARCHAR(10),
            quantity         INT,
            unit_price       DECIMAL(10,2),
            total_amount     DECIMAL(12,2),
            payment_method   VARCHAR(20)
        )""",
    "returns": """
        CREATE TABLE returns (
            return_id      VARCHAR(10) PRIMARY KEY,
            transaction_id VARCHAR(12),
            return_date    DATE,
            reason         VARCHAR(50),
            refund_amount  DECIMAL(12,2)
        )""",
}


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )


def load_table(cursor, table: str, ddl: str) -> int:
    """Drop, recreate, and fill one table from its CSV. Returns row count."""
    csv_path = DATA_DIR / f"{table}.csv"
    df = pd.read_csv(csv_path)

    cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
    cursor.execute(ddl)

    cols = ", ".join(f"`{c}`" for c in df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_sql = f"INSERT INTO `{table}` ({cols}) VALUES ({placeholders})"

    rows = [tuple(r) for r in df.itertuples(index=False, name=None)]
    cursor.executemany(insert_sql, rows)
    return len(rows)


def main():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        for table, ddl in SCHEMAS.items():
            count = load_table(cursor, table, ddl)
            print(f"  loaded {table:<20} {count:>6} rows")
        conn.commit()
        print("\nAll tables loaded successfully.")
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()