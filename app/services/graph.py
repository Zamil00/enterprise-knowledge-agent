from langgraph.graph import END, StateGraph
from app.core.state import AgentState
from app.services.agents import analysis_agent, report_agent, retrieval_agent


def _route_after_analysis(state: AgentState) -> str:
    if state.get("should_block_answer"):
        return "report"
    return "report"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("retrieve", retrieval_agent)
    graph.add_node("analyze", analysis_agent)
    graph.add_node("report", report_agent)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "analyze")
    graph.add_conditional_edges("analyze", _route_after_analysis, {"report": "report"})
    graph.add_edge("report", END)
    return graph.compile()