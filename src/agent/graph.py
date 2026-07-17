"""Wire the stations into a LangGraph. The paper flowchart, running."""

from langgraph.graph import StateGraph, START, END

from src.agent.state import AgentState
from src.agent.nodes import (
    generate_sql,
    validate_sql,
    execute_sql,
    refuse,
    summarize,
    respond_error,
)


def route_after_validation(state: AgentState) -> str:
    """Fork 1: is the SQL safe to run?"""
    return "execute_sql" if state["is_safe"] else "refuse"


def route_after_execution(state: AgentState) -> str:
    """Fork 2: success -> summarize; failure -> retry twice, then apologize."""
    if not state["db_error"]:
        return "summarize"
    return "generate_sql" if state.get("attempts", 0) < 2 else "respond_error"


builder = StateGraph(AgentState)

# ---- Hire the stations ----
builder.add_node("generate_sql", generate_sql)
builder.add_node("validate_sql", validate_sql)
builder.add_node("execute_sql", execute_sql)
builder.add_node("refuse", refuse)
builder.add_node("summarize", summarize)          # the plating chef
builder.add_node("respond_error", respond_error)  # the graceful apology

# ---- Draw the arrows ----
builder.add_edge(START, "generate_sql")
builder.add_edge("generate_sql", "validate_sql")

builder.add_conditional_edges(                    # fork 1: safety
    "validate_sql",
    route_after_validation,
    {"execute_sql": "execute_sql", "refuse": "refuse"},
)

builder.add_conditional_edges(                    # fork 2: execution + retry loop
    "execute_sql",
    route_after_execution,
    {
        "summarize": "summarize",
        "generate_sql": "generate_sql",           # the loop back — with a leash
        "respond_error": "respond_error",
    },
)

builder.add_edge("summarize", END)
builder.add_edge("respond_error", END)
builder.add_edge("refuse", END)

graph = builder.compile()