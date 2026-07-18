"""Chat with the Retail SQL Analyst Agent in a browser. Usage: uv run streamlit run app_streamlit.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from src.agent.graph import graph

st.set_page_config(page_title="Retail SQL Analyst Agent", page_icon="\U0001F4CA")
st.title("Retail SQL Analyst Agent")
st.caption("Ask business questions about the retail dataset — type 'and only for X?' style "
           "follow-ups too.")

if "history" not in st.session_state:
    st.session_state.history = []       # exact shape app.py uses: [{"question","sql","answer"}]
if "display_log" not in st.session_state:
    st.session_state.display_log = []   # richer per-turn data for rendering only

for turn in st.session_state.display_log:
    with st.chat_message("user"):
        st.write(turn["question"])
    with st.chat_message("assistant"):
        if turn["refusal_reason"]:
            st.warning(f"Refused: {turn['refusal_reason']}")
        elif turn["db_error"]:
            st.error(turn["answer"])
        else:
            st.success(turn["answer"])
        if turn["sql"]:
            with st.expander("SQL"):
                st.code(turn["sql"], language="sql")
        if turn["rows"]:
            st.dataframe(turn["rows"])

question = st.chat_input("Ask a business question…")
if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                result = graph.invoke({"question": question, "history": st.session_state.history})
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                result = None

        if result is not None:
            refusal_reason = result.get("refusal_reason", "")
            db_error = result.get("db_error", "")
            answer = result.get("answer", "")
            sql = result.get("sql", "")
            rows = result.get("rows", [])

            if refusal_reason:
                st.warning(f"Refused: {refusal_reason}")
            elif db_error:
                st.error(answer)
            else:
                st.success(answer)
            if sql:
                with st.expander("SQL"):
                    st.code(sql, language="sql")
            if rows:
                st.dataframe(rows)

            st.session_state.history.append({
                "question": question, "sql": sql, "answer": answer,
            })
            st.session_state.display_log.append({
                "question": question, "sql": sql, "answer": answer,
                "rows": rows, "refusal_reason": refusal_reason, "db_error": db_error,
            })
