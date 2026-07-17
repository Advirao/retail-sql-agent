"""Deterministic SQL safety check. No LLM involved — on purpose."""

import re

# Words that mean "this query changes something" — instant rejection
FORBIDDEN = [
    "insert", "update", "delete", "drop", "alter", "create",
    "truncate", "replace", "grant", "revoke", "call", "load",
]


def check_sql(sql: str) -> tuple[bool, str]:
    """Return (is_safe, reason). Reason is empty when safe."""
    cleaned = sql.strip().rstrip(";").strip()

    # Rule 1: must be exactly one statement (no "SELECT ...; DROP ...")
    if ";" in cleaned:
        return False, "Multiple SQL statements are not allowed."

    # Rule 2: must start with SELECT
    if not cleaned.lower().startswith("select"):
        return False, "Only SELECT queries are allowed."

    # Rule 3: no forbidden words anywhere (as whole words)
    for word in FORBIDDEN:
        if re.search(rf"\b{word}\b", cleaned, re.IGNORECASE):
            return False, f"Forbidden keyword detected: {word.upper()}."

    return True, ""