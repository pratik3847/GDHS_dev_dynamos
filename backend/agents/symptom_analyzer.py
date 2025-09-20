import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END   # ✅ works in 0.6.7

# Load environment variables
load_dotenv()

# -------------------------------
# Define Model (LangChain wrapper for OpenRouter)
# -------------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
    api_key=os.getenv("OPENROUTER_API_KEY"),   # ✅ from .env
    base_url="https://openrouter.ai/api/v1"    # ✅ force OpenRouter base URL
)

# -------------------------------
# Prompt Template
# -------------------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a medical reasoning assistant.
Return STRICT JSON only in this schema:
{{
  "top_differentials": [
    {{"name": "string", "rationale": "string"}}
  ],
  "risk_level": "low|moderate|high",
  "disclaimer": "This is AI-generated and not medical advice."
}}
"""),
    ("user", "Patient input:\nSymptoms: {symptoms}\nAge: {age}\nHistory: {history}")
])


# -------------------------------
# Agent Function
# -------------------------------
def symptom_analyzer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node for Symptom Analyzer"""
    chain = prompt | llm
    result = chain.invoke({
        "symptoms": state.get("symptoms", ""),
        "age": state.get("age", ""),
        "history": state.get("history", ""),
    })

    raw_content = result.content.strip()

    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError:
        parsed = {"raw_output": raw_content}

    # Add output back into state
    state["symptom_analysis"] = parsed
    return state

# -------------------------------
# Build Graph (compile workflow)
# -------------------------------
def build_symptom_graph():
    graph = StateGraph(dict)

    # Add Symptom Analyzer node
    graph.add_node("symptom_analyzer", symptom_analyzer_agent)

    # Entry → Symptom Analyzer → End
    graph.set_entry_point("symptom_analyzer")
    graph.add_edge("symptom_analyzer", END)

    return graph.compile()
