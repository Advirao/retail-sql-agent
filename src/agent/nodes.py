"""The agent's stations. First one: the SQL writer."""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from src.agent.state import AgentState
from src.agent.schema import DB_SCHEMA

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

SQL_WRITER_PROMPT = """You are an expert MySQL analyst for a retail company.

{schema}

{history_block}Write ONE read-only MySQL SELECT query that answers the user's question.

Rules:
- SELECT only. Never write INSERT, UPDATE, DELETE, DROP, or any other statement.
- Return ONLY the SQL. No explanations, no markdown fences, no comments.
- Always alias aggregate columns clearly (e.g., SUM(total_amount) AS total_revenue).
- Distinguish counts from amounts: "most/how many returns" means COUNT(return_id);
  "highest refund/how much" means SUM(refund_amount).
- LIMIT results to 50 rows unless the question implies an aggregate.
- If the question is a follow-up (e.g., "and only for Mumbai?"), it refers to the
  question tagged [MOST RECENT] above — reuse THAT query's metric and structure and
  apply the new condition, even if earlier turns in the conversation covered a
  different metric.
- If the question cannot be answered from the retail database schema above
  (it is off-topic or out of scope), return exactly this text and nothing else:
  OUT_OF_SCOPE  
- MySQL does NOT support LIMIT inside IN/ALL/ANY subqueries. For "top N" filtering,
  never use IN with a subquery — instead JOIN a derived table, e.g.:
  JOIN (SELECT id FROM ... ORDER BY metric DESC LIMIT 5) top5 ON t.id = top5.id

User question: {question}
"""


def generate_sql(state: AgentState) -> dict:
    history = state.get("history", [])
    if history:
        recent = history[-3:]
        lines = ["Conversation so far (oldest to most recent):"]
        for i, h in enumerate(recent):
            tag = "MOST RECENT" if i == len(recent) - 1 else f"{len(recent) - i} turns ago"
            lines.append(f"  [{tag}] question: {h['question']}")
            lines.append(f"  [{tag}] SQL: {h['sql']}")
        history_block = "\n".join(lines) + "\n\n"
    else:
        history_block = ""

    if state.get("db_error"):                       # ← retry feedback, its own block
        history_block += (
            "IMPORTANT — your previous attempt failed.\n"
            f"Previous SQL:\n{state['sql']}\n"
            f"MySQL error: {state['db_error']}\n"
            "Rewrite the query to avoid this error. Hint: MySQL does not support "
            "Do NOT use IN (subquery) at all. Replace it with a JOIN onto a derived table: "
            "JOIN (SELECT ... ORDER BY ... LIMIT N) alias ON ... — LIMIT inside FROM is legal.\n\n"
        )

    prompt = SQL_WRITER_PROMPT.format(              # ← format call, clean and separate
        schema=DB_SCHEMA, history_block=history_block, question=state["question"]
    )
    response = llm.invoke(prompt)
    sql = response.content.strip()
    if sql.startswith("```"):
        sql = sql.strip("`").removeprefix("sql").strip()
    return {"sql": sql}

from src.agent.safety import check_sql
from src.agent.db import run_query


def validate_sql(state: AgentState) -> dict:
    if state["sql"].strip().upper() == "OUT_OF_SCOPE":
        return {"is_safe": False,
                "refusal_reason": "That question is outside the retail sales data I can answer from."}
    ok, reason = check_sql(state["sql"])
    return {"is_safe": ok, "refusal_reason": reason}


def execute_sql(state: AgentState) -> dict:
    try:
        rows = run_query(state["sql"])
        return {"rows": rows, "db_error": ""}
    except Exception as e:
        return {"rows": [], "db_error": str(e),
                "attempts": state.get("attempts", 0) + 1}


def respond_error(state: AgentState) -> dict:
    return {"answer": "I generated a query the database couldn't execute, so I have "
                      "no reliable result for this one. Could you rephrase the question? "
                      f"(Technical detail: {state['db_error'][:150]})"}


def refuse(state: AgentState) -> dict:
    return {"answer": f"I can't run that request. {state['refusal_reason']} "
                      "I only answer read-only business questions about the retail data."}
SUMMARY_PROMPT = """You are a retail business analyst writing for a non-technical manager.

The manager asked: {question}

This SQL was run against the MySQL retail database:
{sql}

It returned these rows:
{rows}

Write a concise answer (under 120 words) with exactly three parts:
1. Insight — directly answer the question in plain business language.
2. Evidence — cite the key numbers from the rows (amounts are INR).
3. Caveat — one honest assumption or limitation (e.g., figures are gross
   sales and do not subtract returns, or the data covers Jul 2025 - Jun 2026 only).

Never invent numbers that are not in the rows. No markdown headers, just clear prose.
"""


def summarize(state: AgentState) -> dict:
    rows_text = "\n".join(str(r) for r in state["rows"][:50]) or "No rows returned."
    prompt = SUMMARY_PROMPT.format(
        question=state["question"], sql=state["sql"], rows=rows_text
    )
    response = llm.invoke(prompt)
    return {"answer": response.content.strip()}