from app.agents.tools import research_company, scan_for_jobs
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
    
    for job in high_matches:
        company = job['company']
        if company not in research_notes:
            # need to research
            print(f"Decision: High match found for {company}. Triggering Research.")
            return {"next": "researcher", "target_company": company}
            
    # no research needed
    return {"next": "end"}

async def researcher_node(state: AgentState):
    matches = state["matches"]
    current_notes = state.get("research_notes", {})

    # find highest score company with no research
    target_company = None

    for job in matches:
        score = job.get('match_details', {}).get('score', 0)
        company = job.get('company')
        
        # if score is > 80 and haven't researched it
        if score > 80 and company and company not in current_notes:
            target_company = company
            break
    
    if not target_company:
        print("Worker Warning: No unresearched high matches found.")
        return {"research_notes": current_notes}

    print(f"Researching into: {target_company}")

    # call the research tool
    try:
        research_result = await research_company.ainvoke(target_company)
    except Exception as e:
        print(f"Research failed for {target_company}: {e}")
        research_result = "Research failed or API unavailable."

    # create a new dictionary to ensure clean state updates
    updated_notes = current_notes.copy()
    updated_notes[target_company] = research_result
    
    return {"research_notes": updated_notes}


# build the graph
workflow = StateGraph(AgentState)
# add nodes and entry point
workflow.add_node("scanner", scanner_node)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("researcher", researcher_node)

workflow.set_entry_point("scanner")

workflow.add_edge("scanner", "supervisor")

def route_supervisor(state):
    matches = state["matches"]
    research_notes = state.get("research_notes", {})
    
    high_matches = []
    for m in matches:
        if m["match_details"]["score"] > 80:
            high_matches.append(m)

    for job in high_matches:
        if job['company'] not in research_notes:
            return "researcher"
            
    return "end"

workflow.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {
        "researcher": "researcher",
        "end": END
    }
)

workflow.add_edge("researcher", "supervisor")

app = workflow.compile()