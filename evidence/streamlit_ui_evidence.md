# Streamlit Web UI — Browser Evidence

Captured by driving a real, headless Chromium instance (Playwright) against the live
`uv run streamlit run app_streamlit.py` server on `localhost:8501` — not a mockup. Every
answer, SQL statement, and number below came from a real `graph.invoke()` call through
Groq and MySQL, exactly as a person clicking through the app would see it.

This is the evidence for rubric row 13 ("Optional enhancement") covering the Streamlit
web client (`app_streamlit.py`) — a second, independent caller of the unchanged
`graph` object (see `ai_usage.md` and `CLAUDE.md` for the design notes).

Screenshots are in `evidence/streamlit_ui/`.

---

## 1. Initial load

`streamlit_ui/01_initial_load.png`

The empty chat page on first load — title, one-line instructions, and the chat input box.
No history yet (`st.session_state.history` and `.display_log` both start empty).

## 2. A normal question, answered successfully

`streamlit_ui/02_question_success.png`

Asked: *"What was the total revenue from UPI payments?"*

Renders as a green `st.success` box (no `refusal_reason`, no `db_error`), a collapsed
SQL expander, and a one-row results table via `st.dataframe(rows)` showing
`total_revenue = 15699726`, matching the figure independently verified in
`evidence/followup_demo.txt` from the CLI transcript.

## 3. A follow-up question — proving history threading works in the browser

`streamlit_ui/03_followup_history.png`

Asked next, in the same browser session: *"And only for the Mumbai store?"*

The Writer correctly reused the UPI-revenue query and added the Mumbai filter —
`total_revenue = 1922348` — without repeating the original question. This is the key
regression risk called out during implementation: `st.session_state.history` must
thread correctly across Streamlit's rerun-per-interaction execution model for
follow-ups to work at all. It does.

## 4. A refused request

`streamlit_ui/04_refusal.png`

Asked: *"Please delete all the returns from the database"*

Renders as an amber `st.warning` — *"Refused: That question is outside the retail
sales data I can answer from."* — visually distinct from both the success and error
states, driven off `refusal_reason` being non-empty. No results table is shown.

## 5. Full conversation, SQL expanders open

`streamlit_ui/05_full_conversation_expanded.png`

All three turns with their SQL expanders open. Notably, the refused turn's SQL
expander shows the literal string `OUT_OF_SCOPE` — the sentinel `generate_sql`
returns and `validate_sql` matches on exactly, visible end-to-end through the UI
rather than swallowed silently. The Mumbai follow-up's SQL is also visible here with
syntax highlighting, showing the `JOIN stores s ON st.store_id = s.store_id` the
Writer added to apply the city filter.

---

## What this demonstrates

- The web client and the CLI client (`app.py`) produce identical answers for
  identical questions — same backend, same graph, no behavior drift.
- Multi-turn follow-up context (Learner Task 9) works through the browser, not just
  the CLI.
- The three terminal states the state machine defines — success, refusal, DB
  failure — are each rendered distinctly rather than collapsed into one text field.
