import requests
import asyncio
import re
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from bs4 import BeautifulSoup
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain.agents import create_agent
from typing import List, Dict

GITHUB_URL = "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/README.md"

NOISE_PATTERNS = [
    re.compile(r'Skip to main content.*?(?=\n)', re.IGNORECASE),
    re.compile(r'Sign In.*?(?=\n)', re.IGNORECASE),
    re.compile(r'© \d{4}.*', re.IGNORECASE),
    re.compile(r'Apply\s*locations.*', re.IGNORECASE),
    re.compile(r'Follow Us.*', re.IGNORECASE),
]

@tool(description="This tool gets a certain amount of jobs from the github summer 2026 internships repo")
def get_github_jobs(limit: int=3) -> List[Dict]:
    try:
        r = requests.get(GITHUB_URL, timeout=10)
        # checks for any errors
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        # find table
        table = soup.find('table')

        if not table:
            return {"Error": "No table found"}
        
        body = table.find("tbody")
        rows = body.find_all("tr")
        
        jobs = []
        last_company = ""

        # for each table row, we need to extract the data from each column, td
        for row in rows:
            if len(jobs) >= limit:
                break
            cells = row.find_all("td")
            # check if any rows are bad
            if len(cells) < 4:
                continue
            
            raw_company = cells[0].get_text(strip=True)
            
            # use previous company for arrow
            if '↳' in raw_company or not raw_company:
                company = last_company
            else:
                company = raw_company
                last_company = company
            
            # skip if company name is empty
            if not company:
                continue

            # extract the role
            role = cells[1].get_text(strip=True)

            # extract the location
            location = cells[2].get_text(strip=True)

            # extract the link
            link_tag = cells[3].find("a")
            if link_tag:
                link = link_tag["href"]
            else:
                link = "No link"

            jobs.append({
                "company": company,
                "role": role,
                "location": location,
                "link": link
                })
        return jobs
    except Exception as e:
        return [{"Error": f"Failed to fetch jobs: {str(e)}"}]

# cleans up the markdown file by removing any unneccesary info
def _clean_job_description(markdown_text: str) -> str:    
    cleaned = markdown_text
    for pattern in NOISE_PATTERNS:
        cleaned = pattern.sub('', cleaned)
    
    return cleaned.strip()

# crawl4ai setup
async def _crawl_async(url: str) -> str:
    # create browser config
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
    )
    # create crawler config to wait for sites like workday to load
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        delay_before_return_html=3.0,
        markdown_generator=DefaultMarkdownGenerator(
            options={"ignore_links": True, "ignore_images": True}
        )
    )
    # create instance of async web crawler
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Run the crawler on a URL
        result = await crawler.arun(url=url, config=run_config)
        if result.success:
            return result.markdown
        else:
            return f"Error scraping page: {result.error_message}"

@tool(description="Scrapes a job posting based on a url to get its relevant info such as description, requirements, benefits, etc")
def scrape_job_posting(url: str) -> str:
    try:
        raw_markdown = asyncio.run(_crawl_async(url))
        cleaned_text = _clean_job_description(raw_markdown)
        return cleaned_text
        
    except Exception as e:
        return f"Error scraping job posting: {str(e)}"

@tool(description="Matches a resume to a job description using AI analysis")
def match_resume_to_job(job_description: str, resume_text: str) -> Dict:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    prompt = ChatPromptTemplate.from_template(
        """
        You are a strict technical recruiter. Analyze the match between the Resume and Job Description.
        SCORING GUIDE (be specific and differentiate):
        90-100: Exceptional fit - candidate exceeds multiple key requirements with relevant projects
        75-89: Strong fit - candidate meets most requirements with clear evidence
        60-74: Moderate fit - candidate meets some requirements but has gaps
        40-59: Weak fit - candidate has transferable skills but missing key requirements
        0-39: Poor fit - minimal overlap with requirements
        
        JOB DESCRIPTION:
        {job_description}
        
        CANDIDATE RESUME:
        {resume_text}
        
        STRICT INSTRUCTION:
        You must prove your match score by citing SPECIFIC projects, roles, or tools from the resume. 
        Do not just say "Candidate has experience." Say "Candidate used [Tool] in [Project Name]."
        
        EXAMPLE OF GOOD EVIDENCE:
        "Job requires React -> Candidate used React in 'MeteorMate' project to build the dashboard."
        "Job requires Cloud -> Candidate deployed 'Safe Speak' app using Firebase."

        OUTPUT JSON ONLY:
        {{
            "score": <int 0-100>,
            "reason": "<Summary of fit. Mention the candidate's actual specific project names here.>",
            "evidence": [
                "<Specific Requirement 1> -> <Specific Proof from Resume>",
                "<Specific Requirement 2> -> <Specific Proof from Resume>",
                "<Specific Requirement 3> -> <Specific Proof from Resume>"
            ],
            "missing_skills": ["<skill1>", "<skill2>"]
        }}
        """
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        result = chain.invoke({
            "job_description": job_description[:20000],
            "resume_text": resume_text[:5000]
        })
        return result
        
    except Exception as e:
        return {
            "score": 0, 
            "reason": f"Error: {str(e)}",
            "evidence": [],
            "missing_skills": []
        }
    

def create_job_agent():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=5000)
    tools = [get_github_jobs, scrape_job_posting, match_resume_to_job]
    
    system_prompt="""
    You are a precision Job Hunter. You have access to a user's resume and a list of tools.
    
    YOUR WORKFLOW:
    1. Receive the user's resume and request.
    2. Fetch a list of jobs using `get_github_jobs`.
    3. For each job found (Limit to top 3):
       a. Scrape the full text using `scrape_job_posting`.
       b. Match it against the resume using `match_resume_to_job`.
          - IMPORTANT: You must pass the FULL text of the user's resume to this tool.
    
    4. FINAL OUTPUT REPORT:
    Present the findings in a clean, readable format. 
    For each job, you MUST use the "evidence" field returned by the matching tool.
    
    Format:
    ## [Company Name] - [Role Title] (Score: X/100)
    [Link to Apply]
    **Why it fits:**
    - [Evidence 1 from tool response]
    - [Evidence 2 from tool response]
    
    **Missing:**
    - [Missing Skills from tool response]
    
    Do not use generic summaries. Use the specific project names and details provided by the tools.
    """

    agent = create_agent(
        llm,
        tools,
        system_prompt=system_prompt
    )
    
    return agent

def main():
    MY_RESUME = """
    Nathan Sujatno 
    210-629-2920 | Nathan.sujatno@gmail.com | Richardson, TX 
    github.com/Nsujatno|linkedin.com/in/nathan-sujatno 
    EDUCATION               
    The University of Texas at Dallas, Richardson, TX                                                                             
    Bachelor of Science, Computer Science                                                                                                                                     
    ● Honors & Awards: Academic Excellence Scholar, Hobson Wildenthal Honors College 
    May 2027  
    GPA: 3.8 
    SKILLS                
    Technical Skills: Python, C++, JavaScript, Java | Frameworks: React, Node.js, Express.js, FastAPI, Tailwind CSS | Cloud & 
    Tools: AWS (Lambda, API Gateway, S3, SageMaker), Git, Postman, MongoDB, Supabase 
    EXPERIENCE                
    NRVE intern, Remote                                                                        
    June 2025 – August 2025 
    Backend Project Lead, Frontend Developer           
    ● Architected and deployed a serverless backend on AWS (Lambda, API Gateway, S3) and MongoDB, building 
    scalable RESTful API endpoints in Python. 
    ● Cut database query latency by over 95% by implementing a caching solution with AWS and Cloudflare. 
    ● Contributed to frontend UI development and implemented the full integration layer between backend services 
    and the mobile application. 
    PROJECTS                
    MeteorMate                   
    June 2025 – Current 
    ● Developed a responsive user interface with React.js and Next.js, creating a library of reusable components and 
    leveraging Tailwind CSS for rapid, utility-first styling and a consistent user experience. 
    ● Architected a serverless backend using Firebase for authentication and Supabase, providing secure and scalable 
    RESTful endpoints. 
    Intellect Ink                                  
    February 2025 – May 2025 
    ● Developed a micro-learning app using the MERN tech stack (Express.js, Node.js, MongoDB). 
    ● Developed and integrated RESTful API endpoints with the frontend to produce books, articles, new, poems, and 
    research papers. 
    Kanban Sync, HackUTD                                                                                                                                                
    November 2025  
     Built the backend for an AI-powered workflow assistant used in datacenter operations, enabling natural
    language task creation and validation. 
     Implemented a FastAPI service layer integrated with Supabase for authentication, data storage, and vector 
    embeddings for similarity search. 
     Developed a dual-RAG retrieval pipeline using OpenAI GPT-4o-mini and Ada embeddings to validate instructions 
    against datacenter manuals. 
    LEADERSHIP & ORGANIZATIONS            
    AI MD                                                  
    September 2025 – Current 
    Project Manager 
    ● Leading a student team in developing a full-stack MERN app that utilizes a custom-trained AI model. 
    ● Managed project timelines, delegated tasks, and mentored team members in a collaborative environment. 
    ACM, Officer                                                                                                                                                             
    May 2025 – Current 
    ACM TIP (Technical Interview Prep)                                                                                                        
    ACM, Member                                                                                                                                              
    September 2025 – Current 
    February 2025 – May 2025 
    """

    query = f"""
    Find the latest software engineering internships from the GitHub list.
    Here is my resume:
    {MY_RESUME}
    """

    # call ai agent and allow thought process
    agent_executor = create_job_agent()

    final_response = None

    for event in agent_executor.stream(
        {"messages": [{"role": "user", "content": query}]},
        stream_mode="updates"
    ):
        for node_name, data in event.items():
            print(f"node: {node_name}")
            print("="*20)
            if "messages" in data and data["messages"]:
                last_message = data["messages"][-1]

                final_response = data

                # check if tool call
                if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                    print("Agent decided to call tools:")

                    for tool_call in last_message.tool_calls:
                        print(f"   - Tool: {tool_call['name']}")

    print("final report\n")
    if final_response and "messages" in final_response:
        # last message contains result
        final_message = final_response["messages"][-1]
        if hasattr(final_message, "content"):
            print(final_message.content)
        else:
            print("No final content found")
    else:
        print("No result captured")

if __name__ == "__main__":
    main()