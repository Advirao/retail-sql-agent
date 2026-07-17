"""Attack our own SQL bouncer. Usage: uv run scripts/test_safety.py"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agent.safety import check_sql

attacks = [
    ("SELECT * FROM stores", True),                              # legit
    ("SELECT SUM(total_amount) FROM sales_transactions", True),  # legit
    ("DROP TABLE stores", False),                                # vandal
    ("SELECT 1; DROP TABLE stores", False),                      # smuggler
    ("UPDATE products SET unit_price = 0", False),               # saboteur
    ("  select * from `returns`  ;  ", True),                    # messy but legit
    ("DELETE FROM customers WHERE 1=1", False),                  # eraser
]

for sql, expected in attacks:
    ok, reason = check_sql(sql)
    verdict = "PASS" if ok == expected else "!!! FAIL !!!"
    print(f"{verdict:12} safe={ok!s:5} | {sql[:50]:<52} {reason}")