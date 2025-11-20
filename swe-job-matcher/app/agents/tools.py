import requests
import asyncio
import re
import nest_asyncio
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from bs4 import BeautifulSoup
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain.agents import create_agent
from typing import List, Dict

# allows crawl4ai to work with fastapi
nest_asyncio.apply()

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
    
    system_prompt=system_prompt="""
    You are a precision Job Hunter.
    
    YOUR WORKFLOW:
    1. Fetch top 3 jobs using `get_github_jobs`.
    2. For each job:
       a. Scrape text using `scrape_job_posting`.
       b. Match against resume using `match_resume_to_job`.
    
    CRITICAL FINAL OUTPUT FORMAT:
    You must output a valid JSON string containing a list of the matches.
    Do not output markdown. Do not output conversational text. Just the JSON list.
    
    Example Output structure:
    [
      {
        "company": "Company Name",
        "role": "Job Title",
        "link": "Application URL",
        "match_details": {
            "score": 85,
            "reason": "...",
            "evidence": ["..."],
            "missing_skills": ["..."]
        }
      }
    ]
    """

    agent = create_agent(
        llm,
        tools,
        system_prompt=system_prompt
    )
    
    return agent

async def find_and_match_jobs(resume_text: str) -> List[Dict]:
    agent_executor = create_job_agent()

    query = f"""
    Find the latest software engineering internships.
    Here is my resume:
    {resume_text}
    
    IMPORTANT: Return ONLY a valid JSON array. No markdown, no extra text.
    """

    try:
        # Use ainvoke to get the result
        result = await agent_executor.ainvoke({
            "messages": [{"role": "user", "content": query}]
        })
        
        if "messages" in result and len(result["messages"]) > 0:
            last_message = result["messages"][-1]
            
            # Extract content from the message
            if hasattr(last_message, "content"):
                output_str = last_message.content
            else:
                output_str = str(last_message)
        else:
            raise ValueError("No messages in agent response")
        
        # Clean the output string
        output_str = output_str.replace("``````", "").strip()
        
        # Parse JSON
        matches = json.loads(output_str)
        return matches

    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        print(f"Raw output: {output_str[:500]}")
        return [{
            "company": "Error",
            "role": "Invalid JSON Response",
            "link": "#",
            "match_details": {
                "score": 0, 
                "reason": f"Agent returned invalid JSON: {str(e)}", 
                "evidence": [], 
                "missing_skills": []
            }
        }]
    
    except Exception as e:
        print(f"Agent Execution Error: {e}")
        return [{
            "company": "Error",
            "role": "Agent Failed",
            "link": "#",
            "match_details": {
                "score": 0, 
                "reason": str(e), 
                "evidence": [], 
                "missing_skills": []
            }
        }]