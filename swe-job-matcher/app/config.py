from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pymongo import MongoClient
from clerk_backend_api import Clerk

load_dotenv()

class Settings(BaseSettings):
    openai_api_key: str
    mongo_uri: str
    mongo_db_name: str
    clerk_secret_key: str
    tavily_api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()

try:
    client = MongoClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]
    resumes_collection = db["resumes"]
    users_collection = db["users"]
    jobs_cache_collection = db["jobs_cache"]
    
    print("Connected to MongoDB")

except Exception as e:
    print(f"Could not connect to MongoDB: {e}")

try:
    clerk = Clerk(bearer_auth=settings.clerk_secret_key)
    print("Clerk initialized")
except Exception as e:
    print(f"Could not initialize Clerk: {e}")