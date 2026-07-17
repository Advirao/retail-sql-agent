# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A LangGraph-based agent that answers natural-language retail business questions by generating
read-only MySQL SQL via an LLM (Groq, `llama-3.3-70b-versatile`, temperature 0), validating it
with a deterministic safety check, executing it, and returning a business-language summary.
Built for an "Agentic AI Explorer — Level 2" exercise — see `README.md` for the full writeup
and `ai_usage.md` for documented AI-assisted-development notes and bugs caught in review.

## Commands

Package manager is `uv`; there is no separate lint/build step configured.

```
uv sync                          # install dependencies
uv run scripts/load_data.py      # (re)load the 5 CSVs into MySQL — idempotent, drops+recreates tables
uv run app.py                    # interactive chat REPL with the agent
```

Tests are plain scripts (no pytest), each runnable standalone and printing PASS/FAIL or
inline results — there is no test runner that executes all of them together:

```
uv run scripts/test_safety.py    # adversarial checks against the SQL safety gate (safety.py)
uv run scripts/test_graph.py     # end-to-end: full graph on a couple of sample questions
uv run scripts/test_sql_gen.py   # SQL-generation node in isolation
uv run scripts/test_llm.py       # raw LLM connectivity/sanity check
uv run scripts/test_summary.py   # summarization node in isolation
uv run scripts/hello_graph.py    # minimal LangGraph wiring smoke test
uv run scripts/demo.py           # generates the evidence transcripts in evidence/
```

Setup prerequisites: Python 3.12+, MySQL 8 running locally with `retail_db` created
(`CREATE DATABASE retail_db;`), and a `.env` (copy from `.env.example`) with `GROQ_API_KEY`
and `MYSQL_*` credentials. `.env` is gitignored; never commit it.

## Architecture

The whole agent is a single LangGraph `StateGraph` (`src/agent/graph.py`) over `AgentState`
(`src/agent/state.py`, a `TypedDict`):

```
START → generate_sql → validate_sql →(safe?)→ execute_sql →(ok?)→ summarize → END
                            │ no                   │ error (attempts<2 → generate_sql, else → respond_error)
                            ▼                       ▼
                          refuse                respond_error → END
```

Node implementations all live in `src/agent/nodes.py`:

- **generate_sql** — LLM call. Prompt = `DB_SCHEMA` (`src/agent/schema.py`, hand-written, not
  introspected from MySQL) + up to the last 3 turns of `history` +, on a retry, the previous
  SQL and the MySQL error text explicitly fed back so the model can self-correct. Returns the
  literal string `OUT_OF_SCOPE` when the question can't be answered from this schema.
- **validate_sql** — routes `OUT_OF_SCOPE` straight to refusal; otherwise delegates to
  `src/agent/safety.py::check_sql`, a **deterministic, LLM-free** gate (single statement only,
  must start with `SELECT`, regex-blocklist of INSERT/UPDATE/DELETE/DROP/ALTER/CREATE/
  TRUNCATE/REPLACE/GRANT/REVOKE/CALL/LOAD as whole words). This is intentional defense-in-depth
  — do not replace it with an LLM-based check.
- **execute_sql** — runs the SQL via `src/agent/db.py::run_query` (`mysql-connector-python`),
  hard-capped at 200 rows via `fetchmany(200)`.
- **summarize** — second LLM call; must produce Insight/Evidence/Caveat in ≤120 words and is
  explicitly instructed never to invent numbers not present in the query results.
- **refuse** / **respond_error** — canned graceful-failure responses (no LLM call).

Retry loop: on a DB execution error, the graph loops `execute_sql → generate_sql` up to 2 times
(`state["attempts"]`), feeding the MySQL error back into the next `generate_sql` prompt, before
giving up via `respond_error`. This is how MySQL error 1235 (`LIMIT` inside an `IN (subquery)`,
unsupported) gets self-corrected at runtime — see `ai_usage.md` for the incident.

Conversation memory is **not** handled by LangGraph (no checkpointer is configured). `app.py`
owns a plain `history` list client-side and passes it into `graph.invoke({"question": ...,
"history": history})` on each turn, appending `{question, sql, answer}` after every response.

### Key invariant: schema vs. relationships

MySQL has no actual foreign-key constraints (see `README.md` "Notes & decisions"); table
relationships (`sales_transactions.store_id -> stores.store_id`, etc.) exist only as prose in
`DB_SCHEMA` (`src/agent/schema.py`). If you add/change a table in `scripts/load_data.py`'s
`SCHEMAS` dict, you must also update `DB_SCHEMA` by hand — nothing keeps them in sync
automatically. Also note `returns` is a MySQL reserved word and must stay backtick-quoted
everywhere it's referenced in SQL/prompts.

### Counts vs. amounts

The SQL-writer prompt explicitly distinguishes "most/how many X" (→ `COUNT`) from "highest
value/how much" (→ `SUM`) because the LLM previously conflated them (documented bug in
`ai_usage.md`). Preserve this distinction if you touch `SQL_WRITER_PROMPT` in `nodes.py`.
