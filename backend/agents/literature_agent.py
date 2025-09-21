import os
import json
import requests
from typing import Dict, Any
from dotenv import load_dotenv
from xml.etree import ElementTree as ET

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()

# PubMed endpoints
PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# -------------------------------
# PubMed Fetch Function
# -------------------------------
def fetch_pubmed_articles(query: str, max_results: int = 3):
    """Fetch top PubMed articles with full abstracts."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results
    }
    try:
        search_resp = requests.get(PUBMED_SEARCH_URL, params=params, timeout=10)
        search_resp.raise_for_status()
        search_data = search_resp.json()
    except Exception as e:
        print(f"❌ PubMed search error: {e}")
        return []
    id_list = search_data.get("esearchresult", {}).get("idlist", [])

    if not id_list:
        return []

    fetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml"
    }
    try:
        fetch_resp = requests.get(PUBMED_FETCH_URL, params=fetch_params, timeout=10)
        fetch_resp.raise_for_status()
        root = ET.fromstring(fetch_resp.text)
    except Exception as e:
        print(f"❌ PubMed fetch error: {e}")
        return []

    results = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle", default="No title")
        abstract_texts = [ab.text for ab in article.findall(".//AbstractText") if ab.text]

        abstract = " ".join(abstract_texts).strip()
        results.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract
        })

    return results[:max_results]

# -------------------------------
# LangChain LLM Setup
# -------------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Prompt template for summarizing PubMed abstracts
summary_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a medical research summarizer.
Summarize each abstract into ≤70 words.
Return STRICT JSON as:
{{
  "summaries": [
    {{"pmid": "string", "title": "string", "summary": "string"}}
  ]
}}"""),
    ("user", "Abstracts:\n{abstracts}")
])

# -------------------------------
# Agent Function
# -------------------------------
def literature_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node for Literature Agent (PubMed + LLM summarizer).

    Builds a more specific PubMed query using patient context to improve personalization.
    """
    symptoms = (state.get("symptoms") or "").strip()
    diagnosis = (state.get("diagnosis") or "").strip()
    age = (state.get("age") or "").__str__().strip()
    gender = (state.get("gender") or "").strip()
    medical_history = (state.get("medicalHistory") or state.get("history") or "").strip()
    current_meds = (state.get("currentMedications") or "").strip()

    # Construct targeted PubMed query
    query_terms = []
    if diagnosis:
        query_terms.append(diagnosis)
    if symptoms:
        query_terms.append(symptoms)
    if gender:
        query_terms.append(gender)
    if age:
        query_terms.append(f"age {age}")
    if medical_history:
        query_terms.append(medical_history)
    if current_meds:
        query_terms.append(current_meds)

    query = " AND ".join([t for t in query_terms if t]) or symptoms or diagnosis

    articles = fetch_pubmed_articles(query)

    if not articles:
        state["literature"] = {
            "query": query,
            "articles": [],
            "disclaimer": "No articles found."
        }
        return state

    # Prepare abstracts as input
    abstracts_text = "\n\n".join(
        [f"PMID: {a['pmid']}\nTitle: {a['title']}\nAbstract: {a['abstract']}" for a in articles]
    )

    # If LLM unavailable or fails, provide minimal summaries from abstracts
    parsed = None
    try:
        if os.getenv("OPENROUTER_API_KEY"):
            chain = summary_prompt | llm
            result = chain.invoke({"abstracts": abstracts_text})
            parsed = json.loads((result.content or "").strip())
    except Exception as e:
        print(f"❌ Literature summarizer error: {e}")
        parsed = None
    if parsed is None:
        parsed = {
            "summaries": [
                {
                    "pmid": a.get("pmid", ""),
                    "title": a.get("title", ""),
                    "summary": (a.get("abstract", "")[:500] or "No abstract available.")
                }
                for a in articles
            ]
        }

    state["literature"] = {
        "query": query,
        "articles": parsed,
        "patient_context": {
            "age": age,
            "gender": gender,
            "medical_history": medical_history,
            "current_medications": current_meds,
        },
        "disclaimer": "These references are from PubMed and AI-summarized; verify with a professional."
    }
    return state

# -------------------------------
# Build Graph (standalone version)
# -------------------------------
def build_literature_graph():
    graph = StateGraph(dict)
    graph.add_node("literature_agent", literature_agent)
    graph.set_entry_point("literature_agent")
    graph.add_edge("literature_agent", END)
    return graph.compile()
