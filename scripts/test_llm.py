"""Smoke test: can we reach the Groq LLM? Usage: uv run scripts/test_llm.py"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,          # deterministic as possible — right choice for SQL work
    api_key=os.getenv("GROQ_API_KEY"),
)

response = llm.invoke(
    "In one sentence, what does a retail data analyst do?"
)
print(response.content)