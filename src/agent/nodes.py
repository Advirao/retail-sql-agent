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

Write ONE read-only MySQL SELECT query that answers the user's question.

Rules:
- SELECT only. Never write INSERT, UPDATE, DELETE, DROP, or any other statement.
- Return ONLY the SQL. No explanations, no markdown fences, no comments.
- Always alias aggregate columns clearly (e.g., SUM(total_amount) AS total_revenue).
- LIMIT results to 50 rows unless the question implies an aggregate.

User question: {question}
"""


def generate_sql(state: AgentState) -> dict:
    prompt = SQL_WRITER_PROMPT.format(schema=DB_SCHEMA, question=state["question"])
    response = llm.invoke(prompt)
    sql = response.content.strip()
    if sql.startswith("```"):                    # LLMs love markdown fences; strip them
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