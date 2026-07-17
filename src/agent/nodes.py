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
- If the question is a follow-up (e.g., "and only for Mumbai?"), reuse the metric
  and structure of the previous SQL and apply the new condition.

User question: {question}
"""


def generate_sql(state: AgentState) -> dict:
    history = state.get("history", [])
    if history:
        lines = ["Conversation so far:"]
        for h in history[-3:]:                      # last 3 exchanges is plenty
            lines.append(f"  Previous question: {h['question']}")
            lines.append(f"  Previous SQL: {h['sql']}")
        history_block = "\n".join(lines) + "\n\n"
    else:
        history_block = ""

    prompt = SQL_WRITER_PROMPT.format(
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
    ok, reason = check_sql(state["sql"])
    return {"is_safe": ok, "refusal_reason": reason}


def execute_sql(state: AgentState) -> dict:
    rows = run_query(state["sql"])
    return {"rows": rows}


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