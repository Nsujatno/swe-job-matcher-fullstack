from app.agents.tools import scan_for_jobs
from typing import TypedDict, List
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    resume_text: str
    matches: List[dict]
    research_notes: dict
    messages: List[BaseMessage]

# define nodes in graph
async def scanner_node(state: AgentState):
    results = await scan_for_jobs.ainvoke(state["resume_text"])
    return {"matches": results}

async def supervisor_node(state: AgentState):
    matches = state["matches"]
    research_notes = state.get("research_notes", {})
    high_matches = []
    for m in matches:
        if m["match_details"]["score"] > 80:
            high_matches.append(m)
            
    return {"next": "end"}

# build the graph
workflow = StateGraph(AgentState)
# add nodes and entry point
workflow.add_node("scanner", scanner_node)
workflow.add_node("supervisor", supervisor_node)

workflow.set_entry_point("scanner")

workflow.add_edge("scanner", "supervisor")
workflow.add_edge("supervisor", END)

app = workflow.compile()