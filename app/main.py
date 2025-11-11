from fastapi import FastAPI
from app.config import settings

app = FastAPI()

@app.get("/api/health")
def health_check():
    return {"Good"}

@app.get("/")
def root():
    return {"Hello": "World"}