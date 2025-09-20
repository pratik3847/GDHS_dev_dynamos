import json
from agents.case_matcher import build_case_matcher_graph

if __name__ == "__main__":
    graph = build_case_matcher_graph()

    input_state = {
    "symptoms": "diabetes mellitus"
}


    final_state = graph.invoke(input_state)

    print("\n=== Case Matcher Output ===\n")

    case_results = final_state.get("case_matcher", {})

    matched_cases = case_results.get("matched_cases", [])
    if not matched_cases:
        print("No similar cases found for query:", case_results.get("query", "N/A"))
    else:
        for idx, case in enumerate(matched_cases, 1):
            print(f"Case {idx}:")
            print(f"  ICD Code: {case.get('icd_code', 'N/A')}")
            print(f"  Name: {case.get('name', 'N/A')}")
            print(f"  Description: {case.get('description', 'No description available')}")
            print(f"  Match Score: {case.get('match_score', 'N/A')}")
            print("-" * 80)

    print("\nDisclaimer:", case_results.get("disclaimer", ""))
