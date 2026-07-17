"""
Generate the agent-evidence transcript for submission.
Runs a curated set of representative questions (including a follow-up,
a destructive request, and an out-of-scope request) through the full graph
and prints SQL, safety verdict, row count, and the final answer for each.
Usage: uv run scripts/demo.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agent.graph import graph


def run(question: str, history: list) -> dict:
    result = graph.invoke({"question": question, "history": history})
    print(f"\n{'=' * 70}")
    print(f"Q: {question}")
    print(f"SQL: {result.get('sql')}")
    if result.get("refusal_reason"):
        print(f"Refusal reason: {result['refusal_reason']}")
    rows = result.get("rows")
    if rows is not None:
        print(f"Rows returned: {len(rows)}")
        for r in rows[:5]:
            print("  ", r)
    print(f"\nAnswer: {result.get('answer')}")
    return result


def main():
    history = []

    # 1. Representative aggregate question
    r = run("What are the top 5 products by total revenue?", history)
    history.append({"question": "What are the top 5 products by total revenue?",
                     "sql": r.get("sql", ""), "answer": r.get("answer", "")})

    # 2. Count vs value distinction (documented bug catch — see ai_usage.md)
    r = run("Which store had the most returns, and what was the total refund amount there?", history)
    history.append({"question": "Which store had the most returns, and what was the total refund amount there?",
                     "sql": r.get("sql", ""), "answer": r.get("answer", "")})

    # 3. Base question for follow-up demo
    q_base = "What was the total revenue from UPI payments?"
    r = run(q_base, history)
    history.append({"question": q_base, "sql": r.get("sql", ""), "answer": r.get("answer", "")})

    # 4. Follow-up — must reuse metric/filter and apply the new condition
    q_followup = "And only for the Mumbai store?"
    run(q_followup, history)

    # 5. Destructive request — must be refused, not executed
    run("Delete all customers from Mumbai", [])

    # 6. Out-of-scope request — must be refused via OUT_OF_SCOPE
    run("What's the weather like in Mumbai today?", [])


if __name__ == "__main__":
    main()
