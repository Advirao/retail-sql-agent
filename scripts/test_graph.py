"""The agent answers end-to-end for the first time. Usage: uv run scripts/test_graph.py"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agent.graph import graph

for q in [
    "What are the top 5 products by total revenue?",
    "Drop the sales_transactions table",
]:
    print(f"\n{'='*60}\nQ: {q}")
    result = graph.invoke({"question": q})
    print("SQL:", result.get("sql"))
    print("Safe:", result.get("is_safe"))
    if result.get("rows") is not None:
        for row in result["rows"]:
            print("  ", row)
    if result.get("answer"):
        print("Answer:", result["answer"])