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
    search_resp = requests.get(PUBMED_SEARCH_URL, params=params)
    search_data = search_resp.json()
    id_list = search_data.get("esearchresult", {}).get("idlist", [])

    if not id_list:
        return []

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
    """LangGraph node for Literature Agent (PubMed + LLM summarizer)."""
    query = state.get("symptoms", "") or state.get("diagnosis", "")
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

    chain = summary_prompt | llm
    result = chain.invoke({"abstracts": abstracts_text})

    try:
        parsed = json.loads(result.content.strip())
    except json.JSONDecodeError:
        parsed = {"raw_output": result.content.strip()}

    state["literature"] = {
        "query": query,
        "articles": parsed,
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
