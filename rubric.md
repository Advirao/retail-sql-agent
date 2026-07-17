# Evaluation Rubric (self-authored — none provided by organization)

| # | Capability (from problem statement §4) | Status | Evidence |
|---|---|---|---|
| 1 | Working agent: NL question → data-grounded answer | ✅ | evidence/followup_demo.txt |
| 2 | LangGraph workflow/state | ✅ | src/agent/graph.py (6 nodes, 2 conditional routes, retry cycle) |
| 3 | Free LLM, no secrets exposed | ✅ | Groq via .env; .env gitignored |
| 4 | MySQL as primary source | ✅ | scripts/load_data.py; evidence/data_load_verification.png |
| 5 | Read-only SQL generation & execution | ✅ | transcripts; safety validator |
| 6 | ≥1 follow-up using context | ✅ | "And only for the Mumbai store?" in followup_demo.txt |
| 7 | Validate SQL; refuse destructive/unsafe/out-of-scope | ✅ | safety.py tests; OUT_OF_SCOPE guard; DROP refusal |
| 8 | Concise business summary (insight+evidence+caveat) | ✅ | all transcript answers |
| 13 | Optional enhancement | ✅ | retry loop with error feedback + attempt cap |