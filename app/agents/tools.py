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

job_cache = {}

openai_client = OpenAI(api_key=settings.openai_api_key)
GITHUB_RAW_URL = "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/README.md"

@tool(description="Generates a personalized explanation of why a job matches the user's background")
def explain_job_match(
    company: str,
    title: str,
    job_description: str,
    matched_sections: list,
    match_score: float
) -> str:
    
    top_sections = sorted(
        matched_sections,
        key=lambda x: x['relevance'],
        reverse=True
    )[:3]
    
    sections_text = "\n".join([
        f"- [{section['type']}] (Relevance: {section['relevance']}%): {section['text'][:150]}..."
        for section in top_sections
    ])
    
    # Determine match quality
    if match_score >= 70:
        quality = "excellent"
    elif match_score >= 50:
        quality = "good"
    elif match_score >= 30:
        quality = "moderate"
    else:
        quality = "weak"
    
    # Create prompt for LLM
    prompt = f"""You are a career advisor explaining job match results to a candidate.
        Job: {title} at {company}
        Overall Match Score: {match_score}% ({quality} match)

        Job Description (excerpt):
        {job_description[:600]}...

        Top Matching Resume Sections:
        {sections_text}

        Task: Write a 2-4 sentence explanation that:
        1. States whether this is a good fit and why
        2. Highlights specific overlapping skills or experiences (be specific, mention actual technologies/skills)
        3. If match is low (<50%), mention what key requirements are missing
        4. Keep it encouraging but honest

        Write in second person ("You have experience with..."). Be concise and actionable."""

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        # Fallback explanation if LLM fails
        if match_score >= 70:
            return f"Strong match ({match_score}%)! Your background aligns well with this role's requirements."
        elif match_score >= 50:
            return f"Moderate match ({match_score}%). You have some relevant experience, but may need to highlight transferable skills."
        else:
            return f"Limited match ({match_score}%). This role requires specialized skills that don't strongly align with your current background."

@tool(description="Matches a job against resume using the cached full description")
def match_job_to_resume_by_url(job_url: str, resume_id: str) -> dict:
    # Retrieve full description from cache
    job_description = job_cache.get(job_url)
    
    if not job_description:
        return {
            "match_score": 0,
            "matched_sections": [],
            "error": f"Job not found in cache. Please scrape it first: {job_url}"
        }
    
    print(f"\n[MATCHING] Using cached job ({len(job_description)} chars) for {job_url[:50]}...")
    
    # Now use the full description
    return match_job_to_resume.invoke({
        "job_description": job_description,
        "resume_id": resume_id
    })

@tool(description="Compares a job description against a resume using vector similarity search")
def match_job_to_resume(job_description: str, resume_id: str) -> dict:
    print("\n" + "="*60)
    print("MATCH_JOB_TO_RESUME CALLED")
    print("="*60)
    print(f"Resume ID: {resume_id}")
    print(f"Job Description Length: {len(job_description)} chars")
    print(f"First 300 chars:\n{job_description[:300]}")
    print(f"Last 200 chars:\n{job_description[-200:]}")
    print("="*60 + "\n")
    try:
        # Validate inputs
        if not job_description or len(job_description) < 50:
            return {
                "match_score": 0,
                "matched_sections": [],
                "error": "Job description is too short or empty"
            }
        
        # Step 1: Extract key sections from job description
        job_chunks = _extract_job_chunks(job_description)
        
        if not job_chunks:
            return {
                "match_score": 0,
                "matched_sections": [],
                "error": "Could not extract meaningful sections from job description"
            }
        
        # Step 2: Generate embeddings for each chunk
        embedding_response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=job_chunks  # Multiple chunks at once
        )
        job_embeddings = [item.embedding for item in embedding_response.data]
        
        # Step 3: Query ChromaDB with each chunk
        collection = chroma_client.get_collection(name="resumes")
        
        all_matches = []
        for chunk_embedding, chunk_text in zip(job_embeddings, job_chunks):
            results = collection.query(
                query_embeddings=[chunk_embedding],
                where={"resume_id": resume_id},
                n_results=5,  # Increased to 5 per chunk
                include=["documents", "metadatas", "distances"]
            )
            
            if results['documents'] and results['documents'][0]:
                all_matches.append({
                    "chunk": chunk_text[:100],
                    "distances": results['distances'][0],
                    "documents": results['documents'][0],
                    "metadatas": results['metadatas'][0]
                })
        
        if not all_matches:
            return {
                "match_score": 0,
                "matched_sections": [],
                "message": f"No resume found with ID: {resume_id}"
            }
        
        # Step 4: Calculate scores with skill boosting
        scored_matches = []
        for match in all_matches:
            for distance, metadata in zip(match['distances'], match['metadatas']):
                distance = max(0, min(distance, 2))
                similarity = (1 - (distance / 2)) * 100
                
                # BOOST: Skills chunks get 20% bonus
                if metadata.get('chunk_type') == 'skills':
                    similarity = min(100, similarity * 1.2)
                
                scored_matches.append({
                    "score": max(0, similarity),
                    "type": metadata.get('chunk_type', 'unknown')
                })
        
        # Sort and take top scores
        scored_matches.sort(key=lambda x: x['score'], reverse=True)
        top_scores = [m['score'] for m in scored_matches[:7]]
        
        # Aggressive weighting - top matches matter most
        if len(top_scores) >= 3:
            weights = [0.4, 0.25, 0.15, 0.1, 0.05, 0.03, 0.02][:len(top_scores)]
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
            weighted_score = sum(score * weight for score, weight in zip(top_scores, weights))
        else:
            weighted_score = sum(top_scores) / len(top_scores) if top_scores else 0
        
        # Step 5: Collect matched sections (same as before)
        seen = set()
        matched_sections = []
        for match in all_matches:
            for doc, metadata, dist in zip(match['documents'], match['metadatas'], match['distances']):
                doc_hash = hash(doc)
                if doc_hash not in seen:
                    seen.add(doc_hash)
                    dist = max(0, min(dist, 2))
                    similarity = (1 - (dist / 2)) * 100
                    
                    # Apply same boost to displayed relevance
                    if metadata.get('chunk_type') == 'skills':
                        similarity = min(100, similarity * 1.2)
                    
                    matched_sections.append({
                        "text": doc,
                        "type": metadata.get("chunk_type", "unknown"),
                        "relevance": round(max(0, similarity), 1)
                    })
        
        matched_sections.sort(key=lambda x: x['relevance'], reverse=True)
        matched_sections = matched_sections[:5]
        
        return {
            "match_score": round(weighted_score, 1),
            "matched_sections": matched_sections,
            "message": f"Analyzed {len(job_chunks)} job sections against resume"
        }
        
    except Exception as e:
        return {
            "match_score": 0,
            "matched_sections": [],
            "error": f"Error during matching: {str(e)}"
        }


def _extract_job_chunks(job_description: str) -> list:
    """
    Extracts key sections from a job description for better matching.
    Returns a list of focused text chunks.
    """
    chunks = []
    
    # Keywords that indicate important sections
    important_sections = [
        'requirements', 'qualifications', 'skills', 'experience',
        'responsibilities', 'duties', 'key projects', 'daily tasks',
        'what you', 'you will', 'preferred', 'required', 'must have',
        'looking for', 'seeking', 'candidate will'
    ]
    
    lines = job_description.split('\n')
    current_chunk = []
    capturing = False
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Skip noise sections
        if any(skip in line_lower for skip in ['benefits', 'perks', 'equal opportunity', 'application process', 'about us', 'our mission']):
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
            capturing = False
            continue
        
        # Start capturing at important headers
        if any(keyword in line_lower for keyword in important_sections):
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            capturing = True
        
        # Continue capturing
        elif capturing and line.strip():
            current_chunk.append(line)
            
            # Break chunk if it gets too long (aim for ~300 words per chunk)
            if len('\n'.join(current_chunk)) > 1500:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                capturing = False
    
    # Add last chunk
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    # If no chunks found, fall back to extracting bullet points
    if not chunks:
        bullets = [line.strip() for line in lines if line.strip().startswith(('*', '-', '•'))]
        if bullets:
            # Group bullets into chunks of 10
            for i in range(0, len(bullets), 10):
                chunk = '\n'.join(bullets[i:i+10])
                chunks.append(chunk)
    
    # Last resort: split into paragraphs
    if not chunks:
        paragraphs = [p.strip() for p in job_description.split('\n\n') if len(p.strip()) > 100]
        chunks = paragraphs[:5]  # Take first 5 substantial paragraphs
    
    return chunks[:8]  # Max 8 chunks to avoid API limits

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

async def _crawl_job_async(url: str, max_retries: int = 3) -> str:
    is_workday = "myworkdayjobs.com" in url

    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        user_agent_mode="random",
        extra_args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ]
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
        delay_before_return_html=5.0 if is_workday else 0.5,
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
    job_cache[url] = cleaned
    
    return f"[Job cached as {url}]\n\n{cleaned[:500]}...\n\n[Full description cached for matching]"
    # return cleaned

@tool(description="Scrapes the first 3 job postings from the Summer2026-Internships GitHub README. Returns a list of dicts: {company, title, link}")
def get_first_3_github_jobs() -> list:
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
    
    for row in rows[:3]:
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
        temperature=0,
        max_tokens=4000
    )
    
    tools = [get_first_3_github_jobs, scrape_job_posting, match_job_to_resume, explain_job_match, match_job_to_resume_by_url]
    
    agent = create_agent(
        llm,
        tools,
        system_prompt = """You are an intelligent job recommendation assistant.

            Your workflow:
            1. Get jobs using get_first_3_github_jobs() 
            - EXCEPTION: If the user provides a specific URL, skip this step and only analyze that one job
            
            2. For each job:
            a. Use scrape_job_posting(url) to scrape and cache the full job description
            b. Use match_job_to_resume_by_url(url, resume_id) to match it against the resume
                IMPORTANT: This tool automatically uses the full cached description from step 2a
            c. Store the match results for ranking
            
            3. Sort jobs by match_score (highest to lowest)

            4. For the top 3 jobs with score > 50:
            - Use explain_job_match() to generate personalized explanations
            
            5. Present recommendations with:
            - Company and title
            - Match score percentage
            - Detailed explanation of why it's a good/moderate fit
            - Direct application link

            CRITICAL RULES:
            - Always call scrape_job_posting() BEFORE match_job_to_resume_by_url() for each job
            - Pass the job URL (not the description text) to match_job_to_resume_by_url()
            - If a tool returns an error, acknowledge it briefly and continue with remaining jobs
            - Show your reasoning as you analyze each job

            Error Handling:
            If scraping fails → Note it and skip matching for that job
            If matching fails → Note the error but still present the job with "Unable to calculate match"
            Never stop the entire analysis due to one job failure"""
    )
    
    return agent