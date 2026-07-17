# Retail SQL Data Analyst Agent

A LangGraph-based AI agent that answers natural-language retail business questions
by generating safe, read-only SQL against a MySQL database, and replies with
concise business summaries (insight + evidence + caveat). Built for the
Agentic AI Explorer — Level 2 exercise.

## What it does
- Accepts plain-English questions ("What are the top 5 products by revenue?")
- Generates MySQL SELECT queries via LLM (Groq, Llama 3.3 70B, temperature 0)
- Validates every query with a deterministic safety check (SELECT-only,
  single statement, forbidden-keyword scan) — destructive requests are refused
- Refuses out-of-scope questions via an OUT_OF_SCOPE sentinel
- Executes against MySQL and summarizes results in business language
- Handles follow-up questions using conversation history
  ("And only for the Mumbai store?")
- Retries failed SQL up to 2 times, feeding the MySQL error back to the LLM;
  fails gracefully with an honest message if still unsuccessful

## Architecture
question → generate_sql → validate_sql →(safe?)→ execute_sql →(ok?)→ summarize → answer
                              ↓ no                    ↓ error (≤2 retries → generate_sql)
                            refuse                respond_error

LangGraph state carries: question, sql, is_safe, refusal_reason, rows,
answer, history, db_error, attempts.

## Project structure
- `data/` — 5 synthetic retail CSVs (stores, products, customers,
  sales_transactions, returns)
- `scripts/load_data.py` — creates tables and loads CSVs (idempotent)
- `scripts/test_*.py` — component tests (LLM, safety, SQL gen, graph, summary)
- `src/agent/` — state, schema, safety, db, nodes, graph
- `app.py` — interactive chat loop
- `evidence/` — demo transcripts and validation screenshots
- `docs/` — rubric and AI usage notes

## Setup
1. Prerequisites: Python 3.12+, [uv](https://docs.astral.sh/uv/), MySQL 8
2. Clone the repo
3. `CREATE DATABASE retail_db;` in MySQL
4. Copy `.env.example` to `.env` and fill in your MySQL password and
   [Groq API key](https://console.groq.com) (free)
5. `uv sync`
6. `uv run scripts/load_data.py`   # loads the 5 CSVs into MySQL
7. `uv run app.py`                 # chat with the agent

## Notes & decisions
- **Data**: synthetic datasets (no official LMS data was provided); generated
  with internally consistent foreign keys. Gross sales ₹3.61 cr, refunds ₹20.5 L.
- **LLM fallback**: no organizational LLM gateway was available; fallback is
  Groq free tier (documented per Task 2). Keys live only in `.env` (gitignored).
- **No FK constraints** in MySQL; join relationships are documented in the
  schema prompt (`src/agent/schema.py`) instead.
- Known limitation: "most returns" style questions are validated by count vs
  value distinction in the prompt, but all outputs were human-reviewed
  (see docs/ai_usage.md).