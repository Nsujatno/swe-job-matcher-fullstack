from fastapi import FastAPI
from app.config import settings
from app.routes import resume

app = FastAPI()

app.include_router(resume.router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {"Good"}

@app.get("/")
def root():
    return {"Hello": "World"}