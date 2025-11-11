from pydantic import BaseModel
from typing import Optional, List

class Resume(BaseModel):
    text: str
    skills: Optional[List[str]] = None
    experience: Optional[List[str]] = None
    projects: Optional[List[str]] = None

class UserPreferences(BaseModel):
    role: List[str]
    experience_level: str
    tech_stack: Optional[List[str]]=None
    locations: Optional[List[str]]=None

class JobPosting(BaseModel):
    job_id: str
    company: str
    title: str
    url: str
    description: str
    location: str
    requirements: List[str]
    tech_stack: List[str]

class Recommendation(BaseModel):
    job: JobPosting
    relevance_score: float
    explanation: str
    matched_skills: List[str]
    resume_references: List[str]

class AgentThought(BaseModel):
    step: int
    thought: str
    action: str
    observation: str