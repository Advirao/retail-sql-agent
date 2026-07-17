"""Chat with the Retail SQL Analyst Agent. Usage: uv run app.py"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.agent.graph import graph


def main():
    print("Retail SQL Analyst Agent — ask business questions (type 'exit' to quit)\n")
    history = []
    while True:
        question = input("You: ").strip()
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        result = graph.invoke({"question": question, "history": history})

        print("\n[SQL]", result.get("sql"), "\n")
        print("Agent:", result.get("answer"), "\n")

        history.append({
            "question": question,
            "sql": result.get("sql", ""),
            "answer": result.get("answer", ""),
        })


if __name__ == "__main__":
    main()