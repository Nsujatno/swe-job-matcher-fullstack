from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from app.config import settings

@tool
def get_job_count(input: str) -> str:
    """Get the total number of available job listings."""
    return "There are 5 software engineering internships available right now."

@tool
def get_job_info(job_number: str) -> str:
    """Get information about a specific job by its number (1-5)."""
    jobs = {
        "1": "Google - Software Engineering Intern - Mountain View, CA",
        "2": "Meta - Backend Developer Intern - Menlo Park, CA", 
        "3": "Amazon - SDE Intern - Seattle, WA",
        "4": "Microsoft - Software Engineer Intern - Redmond, WA",
        "5": "Apple - iOS Development Intern - Cupertino, CA"
    }
    
    if job_number in jobs:
        return jobs[job_number]
    else:
        return "Job not found. Please use numbers 1-5."
    
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=settings.openai_api_key
)

# create the agent
tools = [get_job_count, get_job_info]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful job search assistant. Use your tools to answer questions."),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(
    llm, 
    tools,
    prompt
)

# agent executor (handles ReAct loop)
# verbose shows the thinking process
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True
)

# run the agent
def run_agent(question: str):
    """Run the agent and show the ReAct pattern"""
    print(f"\n{'='*60}")
    print(f"USER QUESTION: {question}")
    print(f"{'='*60}\n")
    
    # Invoke the agent - it will automatically loop until done
    result = agent_executor.invoke({"input": question})
    
    print(f"\n{'='*60}")
    print(f"FINAL ANSWER: {result['output']}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    # Example 1: Simple question
    run_agent("How many jobs are available?")
    
    # Example 2: Multiple steps
    run_agent("Tell me about jobs 1, 2, and 3")