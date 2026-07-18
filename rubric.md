# Evaluation Rubric

*Self-authored — no rubric document was provided alongside the problem
statement; §3 of the problem statement lists one as "Provided" but none was
received. Rows 9–12 below were left unfilled in an earlier draft because
their evidence didn't exist yet — see `evidence/` for the files generated to
close that gap.*

## Required Agent Capabilities (problem statement §4)

| # | Capability | Status | Evidence |
|---|---|---|---|
| 1 | Working agent: NL question → data-grounded answer | ✅ | evidence/demo_transcript.txt |
| 2 | LangGraph workflow/state | ✅ | src/agent/graph.py (6 nodes, 2 conditional routes, retry cycle) |
| 3 | Free LLM, no secrets exposed | ✅ | Groq via .env; .env gitignored |
| 4 | MySQL as primary source | ✅ | scripts/load_data.py; evidence/data_load_verification.txt |
| 5 | Read-only SQL generation & execution | ✅ | evidence/demo_transcript.txt; evidence/safety_validation.txt |
| 6 | ≥1 follow-up using context | ✅ | evidence/followup_demo.txt — "And only for the Mumbai store?" |
| 7 | Validate SQL; refuse destructive/unsafe/out-of-scope | ✅ | evidence/safety_validation.txt; evidence/demo_transcript.txt (DROP + weather-question refusals) |
| 8 | Concise business summary (insight+evidence+caveat) | ✅ | all transcript answers in evidence/demo_transcript.txt |

## Learner Tasks (problem statement §5)

| # | Task | Status | Evidence |
|---|---|---|---|
| 9 | Add follow-up context | ✅ | evidence/followup_demo.txt |
| 10 | Demonstrate the agent | ✅ | evidence/demo_transcript.txt |
| 11 | Validate outputs (human review) | ✅ | ai_usage.md (5 documented catches, incl. count-vs-value and follow-up ambiguity, both re-verified in evidence/count_vs_value_verification.txt) |
| 12 | Document enough to run/review | ✅ | README.md, ai_usage.md, this file |
| 13 | Optional enhancement | ✅ | retry loop with error feedback + attempt cap (src/agent/graph.py); Streamlit web UI as a second client (app_streamlit.py) — evidence/streamlit_ui_evidence.md |