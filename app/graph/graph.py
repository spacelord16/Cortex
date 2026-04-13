from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.graph.nodes.supervisor import supervisor_node
from app.graph.nodes.workers import system_worker_node, journal_worker_node, calendar_worker_node, general_worker_node
from app.tools.system import get_system_stats, get_process_list
from langgraph.prebuilt import ToolNode

# Create the graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("SystemWorker", system_worker_node)
workflow.add_node("JournalWorker", journal_worker_node)
workflow.add_node("CalendarWorker", calendar_worker_node)
workflow.add_node("GeneralWorker", general_worker_node)

# Add Tool Node (for System Worker)
system_tools = [get_system_stats, get_process_list]
workflow.add_node("SystemTools", ToolNode(system_tools))

# Supervisor routes to a worker (one-shot — no loop back)
conditional_map = {
    "SystemWorker": "SystemWorker",
    "JournalWorker": "JournalWorker",
    "CalendarWorker": "CalendarWorker",
    "GeneralWorker": "GeneralWorker",
    "FINISH": END
}
workflow.add_conditional_edges("Supervisor", lambda x: x["next"], conditional_map)

# Workers go directly to END — no loop back to Supervisor
# This prevents the Supervisor from re-routing and causing multi-bubble responses.
workflow.add_edge("SystemTools", "SystemWorker")  # Tool output returns to Worker
workflow.add_edge("JournalWorker", END)
workflow.add_edge("CalendarWorker", END)
workflow.add_edge("GeneralWorker", END)

def should_continue(state):
    """After SystemWorker runs: if the LLM made a native tool_call go to tools, else end."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "SystemTools"
    return END  # Go straight to END — answer is ready

workflow.add_conditional_edges("SystemWorker", should_continue)

# Entry Point
workflow.set_entry_point("Supervisor")

graph = workflow.compile()
