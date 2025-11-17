import requests
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

GITHUB_RAW_URL = "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/README.md"

async def _crawl_job_async(url: str) -> str:
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        user_agent_mode="random",
    )
    # strips links and images for cleaning
    md_generator = DefaultMarkdownGenerator(
        options={
            "ignore_links": True,
            "ignore_images": True
        }
    )
    crawl_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=md_generator,
        # for workday websites, need delay
        wait_for="css:[data-automation-id='jobPostingDescription']",
        delay_before_return_html=2,
        js_code="window.scrollTo(0, document.body.scrollHeight);",
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=crawl_config)
        
        if result.success:
            return result.markdown 
        else:
            return f"Error scraping page: {result.error_message}"

@tool(description="Visits a job posting URL, renders the JavaScript, and returns the page content " \
"as Markdown text. Use this to read job descriptions, requirements, and details.")
def scrape_job_posting(url: str) -> str:
    # Run the async function cleanly
    return asyncio.run(_crawl_job_async(url))

@tool(description="Scrapes the first 10 job postings from the Summer2026-Internships GitHub README. Returns a list of dicts: {company, title, link}")
def get_first_10_github_jobs() -> list:
    try:
        response = requests.get(GITHUB_RAW_URL, timeout=30)
        response.raise_for_status()
        md = response.text
    except Exception as e:
        return [{"error": f"Could not fetch README: {e}"}]
    
    soup = BeautifulSoup(md, 'html.parser')
    
    # find the software engineering section
    table = soup.find('table')
    if not table:
        return [{"error": "No table found in README"}]
    
    jobs = []
    
    # Find all rows in tbody
    tbody = table.find('tbody')
    if not tbody:
        return [{"error": "No tbody found in table"}]
    
    rows = tbody.find_all('tr')
    
    for row in rows[:10]:
        cells = row.find_all('td')
        
        if len(cells) < 4:
            continue
        
        # Extract company (cell 0)
        company_cell = cells[0]
        company = company_cell.get_text(strip=True)
        
        # Clean up company name (remove extra symbols)
        company = company.replace('↳', '').strip()
        
        # Skip empty or continuation rows
        if not company or company == '':
            continue
        
        # Extract title (cell 1)
        title = cells[1].get_text(strip=True)
        
        # Extract location (cell 2)
        location = cells[2].get_text(strip=True)
        
        # Extract application link (cell 3)
        app_cell = cells[3]
        link_tag = app_cell.find('a', href=True)
        link = link_tag['href'] if link_tag else None
        
        jobs.append({
            "company": company,
            "title": title,
            "location": location,
            "link": link
        })
        
        if len(jobs) >= 10:
            break
    
    return jobs       



# doc strings are required
# @tool
# def get_job_count(input: str) -> str:
#     """Returns the number of available jobs"""
#     return "There are 5 software engineering internships available right now."

# @tool
# def get_job_info(job_number: str) -> str:
#     """Gets information about a specific job by number (1-5)."""
#     jobs = {
#         "1": "Google - Software Engineering Intern - Mountain View, CA",
#         "2": "Meta - Backend Developer Intern - Menlo Park, CA", 
#         "3": "Amazon - SDE Intern - Seattle, WA",
#         "4": "Microsoft - Software Engineer Intern - Redmond, WA",
#         "5": "Apple - iOS Development Intern - Cupertino, CA"
#     }
    
#     if job_number in jobs:
#         return jobs[job_number]
#     else:
#         return "Job not found. Please use numbers 1-5."

def create_job_agent():
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0
    )
    
    tools = [get_first_10_github_jobs, scrape_job_posting]
    
    agent = create_agent(
        llm,
        tools,
        system_prompt="You are a helpful job search assistant. When a user gives you a job link, use the 'scrape_job_posting' tool to read it before answering questions about requirements."
        # system_prompt="You are a helpful job search assistant who helps users find their perfect software engineering job. Use your tools to answer questions."
    )
    
    return agent