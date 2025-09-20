import json
from orchestrator.orchestrator import build_orchestrator_graph

if __name__ == "__main__":
    graph = build_orchestrator_graph()

    input_state = {
        "symptoms": "persistent cough, chest pain, difficulty breathing",
        "age": 52,
        "history": "smoking for 20 years"
    }

    final_state = graph.invoke(input_state)

    print("\n=== Orchestrator Output ===\n")

    # -------------------------------
    # Symptom Analyzer results
    # -------------------------------
    print(">>> Symptom Analyzer Results:")
    print(json.dumps(final_state.get("symptom_analysis", {}), indent=2))

    # -------------------------------
    # Literature Agent results
    # -------------------------------
    print("\n>>> Literature Agent Results:")

    literature = final_state.get("literature", {})
    parsed = literature.get("articles", {})

    articles = parsed.get("summaries", []) if isinstance(parsed, dict) else []

    if not articles:
        print("No literature found for query:", literature.get("query", ""))
    else:
        for idx, article in enumerate(articles, 1):
            print(f"Article {idx}:")
            print(f"  PMID: {article.get('pmid', 'N/A')}")
            print(f"  Title: {article.get('title', 'No title')}")
            print(f"  Summary: {article.get('summary', 'No summary available')}")
            print("-" * 80)

    print("\nDisclaimer:", literature.get("disclaimer", ""))
