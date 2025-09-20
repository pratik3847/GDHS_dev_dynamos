import os
import json
import requests
from typing import Dict, Any
from dotenv import load_dotenv
from xml.etree import ElementTree as ET

from langgraph.graph import StateGraph, END

# Load env (optional for NCBI API key)
load_dotenv()

# PubMed endpoints
PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# -------------------------------
# PubMed Fetch Function
# -------------------------------
def fetch_pubmed_articles(query: str, max_results: int = 3):
    """Fetch top PubMed articles with abstract snippets (50–70 words)."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results
    }
    # Step 1: Search PubMed for PMIDs
    search_resp = requests.get(PUBMED_SEARCH_URL, params=params)
    search_data = search_resp.json()
    id_list = search_data.get("esearchresult", {}).get("idlist", [])

    if not id_list:
        return []

    # Step 2: Fetch full article details (XML with abstract)
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml"
    }
    fetch_resp = requests.get(PUBMED_FETCH_URL, params=fetch_params)
    root = ET.fromstring(fetch_resp.text)

    results = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle", default="No title")
        abstract_texts = [ab.text for ab in article.findall(".//AbstractText") if ab.text]

        # Join abstract sections into one string
        abstract = " ".join(abstract_texts).strip()

        # Take first 70 words
        words = abstract.split()
        snippet = " ".join(words[:70]) + ("..." if len(words) > 70 else "")

        results.append({
            "pmid": pmid,
            "title": title,
            "abstract_snippet": snippet
        })

    return results[:max_results]

# -------------------------------
# Agent Function
# -------------------------------
def literature_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node for Literature Agent"""
    query = state.get("symptoms", "") or state.get("diagnosis", "")

    articles = fetch_pubmed_articles(query)

    state["literature"] = {
        "query": query,
        "articles": articles,
        "disclaimer": "These references are from PubMed and should be reviewed by a qualified professional."
    }

    return state

# -------------------------------
# Build Graph (standalone version)
# -------------------------------
def build_literature_graph():
    graph = StateGraph(dict)

    # Add Literature Agent node
    graph.add_node("literature_agent", literature_agent)

    # Entry → Literature Agent → End
    graph.set_entry_point("literature_agent")
    graph.add_edge("literature_agent", END)

    return graph.compile()
