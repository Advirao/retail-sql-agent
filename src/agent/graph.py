"""Wire the stations into a LangGraph. The paper flowchart, running."""

from langgraph.graph import StateGraph, START, END

from src.agent.state import AgentState
from src.agent.nodes import (
    generate_sql,
    validate_sql,
    execute_sql,
    refuse,
    summarize,
)


def route_after_validation(state: AgentState) -> str:
    """The fork in the road: read the ticket, name the next station."""
    return "execute_sql" if state["is_safe"] else "refuse"


builder = StateGraph(AgentState)

# ---- Hire the stations ----
builder.add_node("generate_sql", generate_sql)
builder.add_node("validate_sql", validate_sql)
builder.add_node("execute_sql", execute_sql)
builder.add_node("refuse", refuse)
builder.add_node("summarize", summarize)      # the plating chef

# ---- Draw the arrows ----
builder.add_edge(START, "generate_sql")
builder.add_edge("generate_sql", "validate_sql")

builder.add_conditional_edges(                # the decision diamond
    "validate_sql",
    route_after_validation,
    {"execute_sql": "execute_sql", "refuse": "refuse"},
)

builder.add_edge("execute_sql", "summarize")  # arrow in
builder.add_edge("summarize", END)            # arrow out
builder.add_edge("refuse", END)

graph = builder.compile()