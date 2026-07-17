# AI Usage Notes

## How AI was used
- **Claude (Anthropic)**: guided step-by-step learning, code review, debugging
  help, and generation of the synthetic datasets. All code was typed, run, and
  tested by me; errors were diagnosed with AI guidance but fixed by me.
- **Groq / Llama 3.3 70B**: the agent's runtime LLM for SQL generation and
  business summarization (temperature 0).

## Human review performed (Responsible AI / Human in the Loop)
All AI-generated SQL, code, and summaries were reviewed before acceptance.
Documented catches:

1. **Count vs value error**: asked "which store had the most returns," the
   agent returned the store with the highest refund VALUE (Ahmedabad Express,
   ₹273,041, only 16 returns) instead of the most returns by COUNT
   (Delhi Mall, 42). Caught by independent MySQL verification — see
   evidence/count_vs_value_verification.txt. Fix: prompt rule
   distinguishing counts from amounts.
2. **Follow-up context bug**: history was silently dropped because the field
   was not declared on the LangGraph state schema. Diagnosed via debug
   logging; fixed by declaring `history: list` in AgentState.
3. **MySQL 1235 limitation**: LLM repeatedly generated LIMIT inside IN()
   subqueries (unsupported by MySQL). Fixed via prompt rule + retry loop
   feeding the DB error back to the LLM with a derived-table JOIN example.
4. **Number formatting**: summaries occasionally misplace digit-group commas;
   all cited figures were verified against MySQL results.
5. **Follow-up ambiguity with multiple history turns**: while generating
   `evidence/demo_transcript.txt`, asking "And only for the Mumbai store?" after
   three prior questions (two unrelated to the immediately preceding one) caused
   the agent to reuse an earlier turn's metric instead of the most recent one.
   Caught by independent MySQL verification — see
   evidence/count_vs_value_verification.txt and evidence/followup_demo.txt. Fix:
   `generate_sql` now tags each history entry with its recency (`[MOST RECENT]`,
   `N turns ago`) and the prompt rule explicitly says a follow-up refers to the
   `[MOST RECENT]`-tagged turn (src/agent/nodes.py). Re-verified after the fix:
   the follow-up correctly reused the UPI-revenue query and applied the Mumbai
   filter (INR 1,922,348, matching an independently written SQL query).

## Guardrails
- Only synthetic data used; no credentials or client data pasted into AI tools.
- Secrets stored in `.env` (gitignored); `.env.example` documents the shape.