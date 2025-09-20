import json
from agents.symptom_analyzer import build_symptom_graph

if __name__ == "__main__":
    graph = build_symptom_graph()

    input_state = {
        "symptoms": "fever, cough, chest pain",
        "age": 45,
        "history": "smoking 15 pack-years"
    }

    final_state = graph.invoke(input_state)

    # Pretty print JSON
    print(json.dumps(final_state["symptom_analysis"], indent=2))
