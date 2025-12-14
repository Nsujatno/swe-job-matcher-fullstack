from fastapi import FastAPI
from app.config import settings
from app.routes import resume, auth, github_jobs
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(github_jobs.router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {"Good"}

@app.get("/")
def root():
    return {"Hello": "World"}