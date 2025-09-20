import json
from orchestrator.orchestrator import build_orchestrator_graph

if __name__ == "__main__":
    graph = build_orchestrator_graph()

    # ✅ Test case: Diabetes-like symptoms
    input_state = {
        "symptoms": "increased thirst, frequent urination, unexplained weight loss",
        "age": 45,
        "history": "family history of type 2 diabetes"
    }

    final_state = graph.invoke(input_state)

    print("\n=== Orchestrator Output ===\n")

    # -------------------------------
    # Extracted Diagnosis (from Symptom Analyzer)
    # -------------------------------
    print(">>> Extracted Diagnosis (from Symptom Analyzer):")
    print(final_state.get("diagnosis", "No diagnosis extracted"))
    print("-" * 80)

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

    # -------------------------------
    # Case Matcher results
    # -------------------------------
    print("\n>>> Case Matcher Results:")
    case_results = final_state.get("case_matcher", {})
    matched_cases = case_results.get("matched_cases", [])
    if not matched_cases:
        print("No similar cases found.")
    else:
        for idx, case in enumerate(matched_cases, 1):
            print(f"Case {idx}:")
            print(f"  Name: {case.get('name', 'N/A')}")
            print(f"  ICD Code: {case.get('icd_code', 'N/A')}")
            print(f"  Description: {case.get('description', 'N/A')}")
            print(f"  Match Score: {case.get('match_score', 'N/A')}")
            print("-" * 80)
    print("\nDisclaimer:", case_results.get("disclaimer", ""))

    # -------------------------------
    # Treatment Agent results
    # -------------------------------
    print("\n>>> Treatment Agent Results:")
    treatment_results = final_state.get("treatment", {})
    treatments = treatment_results.get("treatments", [])
    if not treatments:
        print("No treatments found.")
    else:
        for idx, treatment in enumerate(treatments, 1):
            print(f"Treatment {idx}:")
            print(f"  Name: {treatment.get('name', 'N/A')}")
            print(f"  Class: {treatment.get('class', 'N/A')}")
            print(f"  Type: {treatment.get('type', 'N/A')}")
            print(f"  Rationale: {treatment.get('rationale', 'N/A')}")
            print(f"  Source: {treatment.get('source', 'N/A')}")
            print("-" * 80)
    print("\nDisclaimer:", treatment_results.get("disclaimer", ""))
