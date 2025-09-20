import json
from agents.symptom_analyzer import build_symptom_graph

if __name__ == "__main__":
    graph = build_symptom_graph()

    # Example patient case (you can edit this for testing)
    input_state = {
    "symptoms": "high fever, severe headache, stiff neck, nausea",
    "age": 28,
    "history": "no significant past medical history"
}


    # Run the graph
    final_state = graph.invoke(input_state)

    # Pretty print output
    print("\n=== Symptom Analyzer Output (with ICD-10-CM India codes) ===\n")
    print(json.dumps(final_state.get("symptom_analysis", {}), indent=2))
