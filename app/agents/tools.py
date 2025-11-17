import requests
import asyncio
import re
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from openai import OpenAI
from app.config import settings, chroma_client

openai_client = OpenAI(api_key=settings.openai_api_key)
GITHUB_RAW_URL = "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/README.md"

@tool(description="Compares a job description against a resume using vector similarity search")
def match_job_to_resume(job_description: str, resume_id: str) -> dict:
    try:
        # generate embedding for job description
        embedding_response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=[job_description]
        )
        job_embedding = embedding_response.data[0].embedding
        collection = chroma_client.get_collection(name="resumes")
        
        results = collection.query(
            query_embeddings=[job_embedding],
            where={"resume_id": resume_id},
            n_results=5,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results['documents'] or not results['documents'][0]:
            return {
                "match_score": 0,
                "matched_sections": [],
                "message": f"No resume found with ID: {resume_id}"
            }
        
        distances = results['distances'][0]
        similarity_scores = []
        for distance in distances:
            distance = max(0, min(distance, 2))
            # Convert: 0 distance = 100% match, 2 distance = 0% match
            similarity = (1 - (distance / 2)) * 100
            similarity_scores.append(max(0, similarity))  # Ensure non-negative
        
        # Weighted average (top matches matter more)
        if len(similarity_scores) >= 3:
            weights = [0.5, 0.3, 0.2][:len(similarity_scores)]
            # Normalize weights
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
            weighted_score = sum(score * weight for score, weight in zip(similarity_scores, weights))
        else:
            weighted_score = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0
        
        # Format matched sections
        matched_sections = []
        for doc, metadata, score in zip(
            results['documents'][0],
            results['metadatas'][0],
            similarity_scores
        ):
            matched_sections.append({
                "text": doc,
                "type": metadata.get("chunk_type", "unknown"),
                "relevance": round(score, 1)
            })
        
        return {
            "match_score": round(weighted_score, 1),
            "matched_sections": matched_sections,
            "message": f"Successfully matched against {len(matched_sections)} resume sections"
        }
        
    except Exception as e:
        return {
            "match_score": 0,
            "matched_sections": [],
            "error": f"Error during matching: {str(e)}"
        }

def _clean_job_description(markdown_text: str) -> str:
    """
    Removes common boilerplate and noise from scraped job postings.
    Keeps only the relevant job content.
    """
    
    # Remove common noise patterns
    noise_patterns = [
        r'Skip to main content.*?(?=\n#{1,3})',  # Navigation
        r'Follow Us.*',  # Footer social links
        r'© \d{4}.*',  # Copyright
        r'Sign In.*?(?=\n)',  # Sign in links
        r'Apply\s*locations.*?(?=\n#{2,3})',  # Apply button section
        r'Careers Home.*?(?=\n)',  # Career site navigation
        r'Know Your Rights.*',  # Legal boilerplate
        r'Read More\s*$',  # Footer links
    ]
    
    cleaned = markdown_text
    for pattern in noise_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.DOTALL)
    
    # Extract only the key sections
    sections_to_keep = []
    lines = cleaned.split('\n')
    
    keep_keywords = [
        'job description', 'your role', 'responsibilities', 'requirements',
        'qualifications', 'you\'re the right fit', 'skills', 'experience',
        'about the role', 'what you\'ll do'
    ]
    
    capture = False
    current_section = []
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Start capturing at relevant headers
        if any(keyword in line_lower for keyword in keep_keywords):
            if current_section:
                sections_to_keep.append('\n'.join(current_section))
            current_section = [line]
            capture = True
        
        # Stop at footer/legal sections
        elif any(stop in line_lower for stop in ['equal employment', 'about us', 'follow us', 'workday, inc']):
            if current_section:
                sections_to_keep.append('\n'.join(current_section))
            break
        
        # Keep capturing if we're in a relevant section
        elif capture and line.strip():
            current_section.append(line)
    
    if current_section:
        sections_to_keep.append('\n'.join(current_section))
    
    return '\n\n'.join(sections_to_keep)

async def _crawl_job_async(url: str) -> str:
    is_workday = "myworkdayjobs.com" in url

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
        wait_for="css:[data-automation-id='jobPostingDescription']" if is_workday else "css:body",
        delay_before_return_html=2.0 if is_workday else 0.5,
        js_code="window.scrollTo(0, document.body.scrollHeight);" if is_workday else None,
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
    # run the async function cleanly
    raw_markdown = asyncio.run(_crawl_job_async(url))

    cleaned = _clean_job_description(raw_markdown)
    
    return cleaned

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

def create_job_agent():
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0
    )
    
    tools = [get_first_10_github_jobs, scrape_job_posting]
    
    agent = create_agent(
        llm,
        tools,
        system_prompt="You are a helpful job search assistant who helps users find their perfect software engineering job. Use your tools to answer questions."
    )
    
    return agent