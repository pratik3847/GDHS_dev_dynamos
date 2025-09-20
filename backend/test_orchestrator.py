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

    # Print Symptom Analyzer results
    print(">>> Symptom Analyzer Results:")
    print(json.dumps(final_state.get("symptom_analysis", {}), indent=2))

    print("\n>>> Literature Agent Results:")
    print(json.dumps(final_state.get("literature", {}), indent=2))
