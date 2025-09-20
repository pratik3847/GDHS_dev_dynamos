import json
from langgraph.graph import StateGraph, END

# Import both agents
from agents.symptom_analyzer import symptom_analyzer_agent
from agents.literature_agent import literature_agent

# -------------------------------
# Orchestrator Graph
# -------------------------------
def build_orchestrator_graph():
    graph = StateGraph(dict)

    # Add both agents as nodes
    graph.add_node("symptom_analyzer", symptom_analyzer_agent)
    graph.add_node("literature_agent", literature_agent)

    # Flow: Entry → Symptom Analyzer → Literature Agent → End
    graph.set_entry_point("symptom_analyzer")
    graph.add_edge("symptom_analyzer", "literature_agent")
    graph.add_edge("literature_agent", END)

    return graph.compile()
