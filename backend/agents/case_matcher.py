import os
import json
import requests
from typing import Dict, Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
BIOPORTAL_API_KEY = os.getenv("BIOPORTAL_API_KEY")  # ✅ Must be set in .env

BIOPORTAL_API_URL = "https://data.bioontology.org/search"

# -------------------------------
# Fetch Case Matches from BioPortal
# -------------------------------
def fetch_case_matches(query: str, max_results: int = 5):
    """Search BioPortal API for ICD/SNOMED/MeSH terms related to query."""
    params = {
        "q": query,
        "ontologies": "ICD10CM,SNOMEDCT,MSH",
        "apikey": BIOPORTAL_API_KEY,
        "pagesize": max_results,
    }
    try:
        response = requests.get(BIOPORTAL_API_URL, params=params, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error fetching BioPortal results: {e}")
        return []

    data = response.json()
    results = []
    for item in data.get("collection", []):
        results.append({
            "icd_code": item.get("notation", "N/A"),
            "name": item.get("prefLabel", "Unknown"),
            "description": (item.get("definition") or ["No description available"])[0],
            "score": item.get("score", 0),
        })

    return results[:max_results]

# -------------------------------
# LangChain LLM Setup
# -------------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
    api_key=os.getenv("OPENROUTER_API_KEY"),   # ✅ OpenRouter key
    base_url="https://openrouter.ai/api/v1"
)

# Prompt for refinement
matcher_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a clinical case matcher AI.
Given ontology results, pick the **top 3 most relevant matches**.
Return STRICT JSON in this schema:
{{
  "matched_cases": [
    {{"icd_code": "string", "name": "string", "description": "string", "match_score": float}}
  ]
}}"""),   # 👈 Escaped curly braces
    ("user", "Ontology results:\n{results}")
])

# -------------------------------
# Agent Function
# -------------------------------
def case_matcher_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node for Case Matcher Agent (BioPortal + LLM refinement)."""
    query = state.get("symptoms", "") or state.get("diagnosis", "")
    if not query:
        state["case_matcher"] = {
            "matched_cases": [],
            "disclaimer": "No query provided."
        }
        return state

    raw_results = fetch_case_matches(query)

    if not raw_results:
        state["case_matcher"] = {
            "matched_cases": [],
            "disclaimer": "No matches found from BioPortal."
        }
        return state

    # Send ontology results to LLM for ranking & selection
    chain = matcher_prompt | llm
    result = chain.invoke({"results": json.dumps(raw_results, indent=2)})

    try:
        parsed = json.loads(result.content.strip())
    except json.JSONDecodeError:
        parsed = {"matched_cases": [], "raw_output": result.content.strip()}

    state["case_matcher"] = {
        "query": query,
        "matched_cases": parsed.get("matched_cases", []),
        "disclaimer": "Ontology matches are retrieved via BioPortal (ICD/SNOMED/MeSH) and AI-refined. Verify clinically."
    }
    return state

# -------------------------------
# Build Graph (standalone version)
# -------------------------------
def build_case_matcher_graph():
    graph = StateGraph(dict)
    graph.add_node("case_matcher", case_matcher_agent)
    graph.set_entry_point("case_matcher")
    graph.add_edge("case_matcher", END)
    return graph.compile()
