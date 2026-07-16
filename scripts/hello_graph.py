"""
My first LangGraph: two nodes, straight-line flow.
Usage: uv run scripts/hello_graph.py
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# ---------- 1. THE STATE: the "order ticket" ----------
# A TypedDict just declares the ticket's fields and their types.
class TicketState(TypedDict):
    question: str    # written by the customer (us)
    shouted: str     # written by node 1
    answer: str      # written by node 2


# ---------- 2. THE NODES: the "stations" ----------
# A node is a plain function: takes the whole ticket,
# returns ONLY the fields it wants to add/update.

def shout_node(state: TicketState) -> dict:
    print("  [shout_node] received:", state["question"])
    return {"shouted": state["question"].upper() + "!!!"}

def answer_node(state: TicketState) -> dict:
    print("  [answer_node] received:", state["shouted"])
    return {"answer": f"You seem excited about: {state['shouted']}"}


# ---------- 3. THE GRAPH: wire stations with edges ----------
builder = StateGraph(TicketState)

builder.add_node("shout", shout_node)
builder.add_node("answer", answer_node)

builder.add_edge(START, "shout")     # ticket enters at shout station
builder.add_edge("shout", "answer")  # then flows to answer station
builder.add_edge("answer", END)      # then leaves the kitchen

graph = builder.compile()


# ---------- 4. RUN: hand a ticket to the kitchen ----------
if __name__ == "__main__":
    result = graph.invoke({"question": "what were my top products"})
    print("\nFinal ticket:", result)