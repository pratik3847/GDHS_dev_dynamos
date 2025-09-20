import json
from agents.treatment_agent import build_treatment_graph

if __name__ == "__main__":
    graph = build_treatment_graph()

    input_state = {
        "diagnosis": "Type 2 Diabetes Mellitus"
    }

    final_state = graph.invoke(input_state)

    print("\n=== Treatment Agent Output ===\n")

    treatment = final_state.get("treatment", {})
    treatments = treatment.get("treatments", [])

    if not treatments:
        print("No treatments found for query:", treatment.get("query", ""))
    else:
        for idx, t in enumerate(treatments, 1):
            print(f"Treatment {idx}:")
            print(f"  Name: {t.get('name', 'N/A')}")
            print(f"  Class: {t.get('class', 'N/A')}")
            print(f"  Type: {t.get('type', 'N/A')}")
            print(f"  Rationale: {t.get('rationale', 'N/A')}")
            print(f"  Source: {t.get('source', 'N/A')}")
            print("-" * 80)

    print("\nDisclaimer:", treatment.get("disclaimer", ""))
