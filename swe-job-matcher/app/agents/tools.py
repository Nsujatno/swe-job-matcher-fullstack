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
from langchain_community.tools import TavilySearchResults
from typing import List, Dict
from app.config import jobs_cache_collection 
from datetime import datetime

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
            
            # Skip rows with the arrow icon (sub-listings)
            if '↳' in raw_company:
                continue
            
            # Skip if company name is empty
            if not raw_company:
                continue
            
            # Set the company name
            company = raw_company

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

def scrape_job_posting(url: str) -> str:
    cached_job = jobs_cache_collection.find_one({"_id": url})
    
    if cached_job:
        print(f"CACHE HIT (DB): Fetching {url} from MongoDB.")
        return cached_job["markdown"]

    print(f"CACHE MISS: Scraping {url}...")
    try:
        raw_markdown = asyncio.run(_crawl_async(url))
        cleaned_text = _clean_job_description(raw_markdown)

        jobs_cache_collection.insert_one({
            "_id": url,
            "markdown": cleaned_text,
            "created_at": datetime.now()
        })
        return cleaned_text
        
    except Exception as e:
        return f"Error scraping job posting: {str(e)}"

def match_resume_to_job(job_description: str, resume_text: str) -> Dict:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = ChatPromptTemplate.from_template(
        """
        You are a Cynical Engineering Manager. You are skeptical of resumes and strictly evaluate candidates based on PROVEN experience, not just keyword mentions.
        
        YOUR GOAL: Find the gaps. Do not gloss over missing skills.
        
        CRITICAL RULES FOR SCORING:
        1. **Experience Level Match (Crucial):**
           - If the Job is "Senior/Lead" and the Resume is "Student/Intern" -> INSTANT FAIL (Score < 50).
           - Even if they have the keywords (React, Python), a student cannot lead a senior team.
           - If Job is "Internship", judge based on potential and project complexity.

        2. **Professional vs. Academic:**
           - Professional Experience > Personal Projects > Class Projects.
           - If a job asks for "Production Experience" and the candidate only has "Personal Projects", deduct points.

        3. **Technical Equivalencies (Keep this):**
           - Tailwind = CSS (Match)
           - Supabase = SQL/Database (Match)
           - Git = GitHub (Match)
        
        4. **Scoring Rubric (Be Harsh):**
           - 100: Impossible (Reserved for perfection).
           - 90-99: "Unicorn" Candidate. Exceeds requirements, has live production apps with users, perfectly matches stack.
           - 80-89: Strong Match. Meets all MUST-HAVES. Maybe misses a "Nice-to-have".
           - 70-79: Good Match. Meets core tech but lacks specific domain knowledge or depth.
           - 60-69: Okay. Has the language (e.g., Python) but wrong framework or context.
           - < 60: Mismatch. Junior applying for Senior, or completely different stack.

        JOB DESCRIPTION:
        {job_description}
        
        CANDIDATE RESUME:
        {resume_text}
        
        INSTRUCTIONS FOR EVIDENCE:
        - Cite the specific project type (Internship vs Project). 
        - Example: "Job requires AWS -> Candidate used AWS in 'NRVE' (Internship) to build serverless backend." (Strong Evidence)
        - Example: "Job requires AWS -> Candidate used AWS in 'MeteorMate' (Personal Project)." (Weaker Evidence)
        
        OUTPUT JSON ONLY:
        {{
            "score": <int 0-100>,
            "reason": "Candidate matches [Seniority Level]. Strongest match is [Skill], weakest area is [Gap].",
            "evidence": [
                "Job requires [Req] -> Match: [Evidence]",
                "Job requires [Req] -> Match: [Evidence]"
            ],
            "missing_skills": ["<List Gaps Here>"]
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
    You are a specialized Job Fetching Agent.
    
    YOUR WORKFLOW:
    1. Call `get_github_jobs` to get the top 3 links.
    2. For EACH job found:
       a. Call `scrape_job_posting` to get the full text.
       b. Call `match_resume_to_job` passing the FULL job text and FULL resume text.
    
    CRITICAL OUTPUT RULES:
    1. You represent the final API response. You must output a VALID JSON ARRAY.
    2. Do NOT include markdown formatting like ```json ... ```.
    3. Do NOT add conversational filler like "Here are your results".
    4. Just output the raw list.
    
    Example Final Output:
    [
      {
        "company": "Google",
        "role": "Software Engineer",
        "link": "...",
        "match_details": { ... result from match tool ... }
      }
    ]
    """

    agent = create_agent(
        llm,
        tools,
        system_prompt=system_prompt
    )
    
    return agent

# helper function to process one job
async def process_single_job(job: Dict, resume_text: str) -> Dict:
    try:
        company = job.get("company")
        role = job.get("role")
        link = job.get("link")

        # in mongodb
        if link and link != "No link":
            description = await asyncio.to_thread(scrape_job_posting, link)
        else:
            description = "No link provided, cannot analyze."
        
        match_result = await asyncio.to_thread(
            match_resume_to_job,
            description,
            resume_text
        )

        return {
            "company": company,
            "role": role,
            "link": link,
            "match_details": match_result
        }
    
    except Exception as e:
        print(f"Error processing {job.get('company')}: {e}")
        return {
            "company": job.get("company", "Unknown"),
            "role": job.get("role", "Unknown"),
            "link": job.get("link", "#"),
            "match_details": {
                "score": 0, 
                "reason": "Error during processing", 
                "evidence": [], 
                "missing_skills": []
            }
        }
    
async def find_and_match_jobs(resume_text: str) -> List[Dict]:
    jobs = get_github_jobs(limit=3)

    if not jobs or "Error" in jobs[0]:
        print("Failed to fetch jobs list.")
        return []
    
    tasks = []
    for job in jobs:
        tasks.append(process_single_job(job, resume_text))

    results = await asyncio.gather(*tasks)
    return results

@tool(description="Scans the github repo, scrapes the top jobs, and matches them against the resume. Returns a list of job matches with scores.")
async def scan_for_jobs(resume_text: str):
    return await find_and_match_jobs(resume_text)

@tool(description="Searches for recent news, engineering blog posts, and financial health of a specific company")
def research_company(company_name: str):
    search = TavilySearchResults(max_results=3)
    return search.invoke(f"{company_name} engineering culture recent news")