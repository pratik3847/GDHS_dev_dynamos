import json
from agents.literature_agent import build_literature_graph

if __name__ == "__main__":
    graph = build_literature_graph()

    input_state = {
        "symptoms": "chronic cough AND tuberculosis"
    }

    final_state = graph.invoke(input_state)

    print("\n=== Literature Agent Output (PubMed + LLM Summarizer) ===\n")

    literature = final_state.get("literature", {})
    parsed = literature.get("articles", {})

    # LLM returns JSON with "summaries"
    articles = parsed.get("summaries", []) if isinstance(parsed, dict) else []

    if not articles:
        print("No articles found for query:", literature.get("query", ""))
    else:
        for idx, article in enumerate(articles, 1):
            print(f"Article {idx}:")
            print(f"  PMID: {article.get('pmid', 'N/A')}")
            print(f"  Title: {article.get('title', 'No title')}")
            print(f"  Summary: {article.get('summary', 'No summary available')}")
            print("-" * 80)

    # Print disclaimer at the end
    print("\nDisclaimer:", literature.get("disclaimer", ""))
