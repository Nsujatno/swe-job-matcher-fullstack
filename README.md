# SWE Job Matcher
## AI-Powered Resume Analysis & Job Matching Agent

SWE Job Matcher is a full-stack application that automates the gap analysis between a candidate's resume and live job postings. Unlike simple keyword matchers, SWE Job Matcher utilizes an autonomous AI Agent to scrape real-time job data, parse complex job descriptions, and perform a "Cynical Engineering Manager" level analysis to provide strict, evidence-based scoring.

# View demo:
https://youtu.be/_XyECzmRpuQ

# The Problem
Most job matching tools rely on basic keyword density (e.g., "Resume has Python 5 times"). They fail to understand context, technical hierarchies (e.g., Tailwind is CSS), or soft skill evidence.

# The Solution
SWE Job Matcher fetches the latest internships from GitHub, crawls the actual application portals (Workday, Greenhouse, Lever), and uses an LLM Agent to:
- Contextualize Skills: Recognizes that "Supabase" counts as "SQL experience."
- Verify Evidence: Only credits skills if they are tied to specific projects or work experience.
- Strict Scoring: Applies a penalty logic for "Student" vs "Professional" experience levels.

# System Architecture
The application uses an Event-Driven Architecture to handle long-running AI tasks without blocking the UI.

# Data Flow:

**Frontend**: User uploads PDF via Next.js (Drag & Drop).

**API Layer**: FastAPI receives the file and immediately offloads the work to a Background Task.

**The Agent**:
- Tool 1: Fetches top jobs from SimplifyJobs/Summer2026-Internships.
- Tool 2 (Scraper): Uses Crawl4AI to scrape the full job description. Includes MongoDB caching to prevent redundant network requests.
- Tool 3 (Matcher): GPT-4o-mini evaluates the fit using a "Cynical Recruiter" system prompt.

# Tech Stack
**Frontend**
- Framework: Next.js
- Language: TypeScript
- Styling: Tailwind CSS (Glassmorphism UI)
- Auth: Clerk

**Backend**
- Framework: Python FastAPI
- Database: MongoDB
- AI Orchestration: LangChain
- LLM: OpenAI GPT-4o-mini
- Scraping: Crawl4AI (Async Web Crawler)

# AI Engineering Highlights
The "Cynical Recruiter" Persona
To prevent LLM hallucinations and "people-pleasing" scores, the matching agent is prompted with strict constraints:
- **Burden of Proof**: Skills are considered missing unless explicitly proven in the resume text.
- **Level Matching**: A "Senior" role is an instant fail for a "Student" resume, regardless of keyword matches.
- **Inference Logic**: The model is instructed to understand equivalencies (e.g., Git matches GitHub, Postgres matches Database).

# Caching Layer
To optimize performance and respect rate limits, scraped job descriptions are cached in MongoDB.

# Future Improvements
[ ] Resume Tailoring: an AI agent that re-writes the resume bullet points to match the job.

[ ] User History: A persistent dashboard of all past scans (partially implemented).

# Author
Nathan Sujatno
