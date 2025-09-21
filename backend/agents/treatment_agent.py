import os
import json
import requests
from typing import Dict, Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

# -------------------------------
# Load environment
# -------------------------------
load_dotenv()

RXNORM_API = "https://rxnav.nlm.nih.gov/REST/drugs.json"

# -------------------------------
# Fetch drugs from RxNorm
# -------------------------------
def fetch_drug_treatments(query: str, max_results: int = 5):
    """Query RxNorm API to fetch drug treatments for a condition or drug name."""
    try:
        response = requests.get(RXNORM_API, params={"name": query}, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error fetching RxNorm results: {e}")
        return []

    data = response.json()
    results = []
    for group in data.get("drugGroup", {}).get("conceptGroup", []):
        for concept in group.get("conceptProperties", []) or []:
            results.append({
                "rxcui": concept.get("rxcui", "N/A"),
                "name": concept.get("name", "Unknown"),
                "class": group.get("tty", "Unknown"),
            })

    return results[:max_results]

# -------------------------------
# LangChain LLM setup
# -------------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# ✅ Escaped JSON braces inside the system prompt
treatment_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a medical treatment recommender.
Given drug results + condition, suggest BOTH drug and non-drug interventions.
Incorporate patient context (age, gender, medical history, current medications) to note contraindications, interactions, and tailoring.
Output STRICT JSON:
{{
    "treatments": [
        {{"name": "string", "class": "string", "type": "drug/non-drug", "rationale": "string", "source": "string"}}
    ]
}}"""),
        ("user", "Condition: {condition}\nAge: {age}\nGender: {gender}\nMedical History: {medical_history}\nCurrent Medications: {current_meds}\nDrug Results:\n{results}")
])

# -------------------------------
# Agent Function
# -------------------------------
def treatment_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node for Treatment Agent."""
    query = state.get("diagnosis", "") or state.get("symptoms", "")
    if not query:
        state["treatment"] = {"treatments": [], "disclaimer": "No input provided."}
        return state

    drug_results = fetch_drug_treatments(query)

    parsed = None
    try:
        if os.getenv("OPENROUTER_API_KEY"):
            chain = treatment_prompt | llm
            result = chain.invoke({
                "condition": query,
                "age": (state.get("age") or ""),
                "gender": (state.get("gender") or ""),
                "medical_history": (state.get("medicalHistory") or state.get("history") or ""),
                "current_meds": (state.get("currentMedications") or ""),
                "results": json.dumps(drug_results, indent=2)
            })
            parsed = json.loads((result.content or "").strip())
    except Exception as e:
        print(f"❌ Treatment LLM error: {e}")
        parsed = None

    if parsed is None:
        # Minimal passthrough list from RxNorm
        parsed = {
            "treatments": [
                {
                    "name": r.get("name", "Unknown"),
                    "class": r.get("class", "Unknown"),
                    "type": "drug",
                    "rationale": "Listed based on RxNorm lookup; details unavailable in dev mode.",
                    "source": "RxNorm"
                }
                for r in drug_results
            ]
        }

    state["treatment"] = {
        "query": query,
        "treatments": parsed.get("treatments", []),
        "patient_context": {
            "age": state.get("age"),
            "gender": state.get("gender"),
            "medical_history": state.get("medicalHistory", state.get("history")),
            "current_medications": state.get("currentMedications"),
        },
        "disclaimer": "AI + RxNorm suggestions personalized by patient context. In development, outputs may be simplified if API keys are missing. Verify with clinical guidelines."
    }
    return state

# -------------------------------
# Build Graph (standalone)
# -------------------------------
def build_treatment_graph():
    graph = StateGraph(dict)
    graph.add_node("treatment_agent", treatment_agent)
    graph.set_entry_point("treatment_agent")
    graph.add_edge("treatment_agent", END)
    return graph.compile()
