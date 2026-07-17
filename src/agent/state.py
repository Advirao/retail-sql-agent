"""The order ticket that flows through the agent."""

from typing import TypedDict


class AgentState(TypedDict):
    question: str        # what the user asked
    sql: str             # SQL written by the LLM
    is_safe: bool        # verdict from the bouncer
    refusal_reason: str  # why the bouncer said no (if it did)
    rows: list           # results from MySQL
    answer: str          # final business summary
    history: list        # previous exchanges: {"question", "sql", "answer"}
    db_error: str        # MySQL's complaint, if execution failed
    attempts: int        # how many times SQL generation has been tried