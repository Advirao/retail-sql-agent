"""Run read-only SQL against MySQL and return rows."""

import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def run_query(sql: str) -> list[dict]:
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )
    try:
        cursor = conn.cursor(dictionary=True)   # rows come back as dicts
        cursor.execute(sql)
        return cursor.fetchmany(200)            # hard cap: never flood the ticket
    finally:
        conn.close()