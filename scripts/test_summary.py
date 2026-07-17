"""Full pipeline with business summaries. Usage: uv run scripts/test_summary.py"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agent.graph import graph

for q in [
    "What are the top 5 products by total revenue?",
    "Which store had the most returns, and what was the total refund amount there?",
]:
    print(f"\n{'='*60}\nQ: {q}")
    result = graph.invoke({"question": q})
    print("SQL:", result.get("sql"), "\n")
    print("ANSWER:", result.get("answer"))