from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

class Settings(BaseSettings):
    openai_api_key: str
    mongo_uri: str
    mongo_db_name: str
    
    class Config:
        env_file = ".env"

settings = Settings()

try:
    client = MongoClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]
    resumes_collection = db["resumes"]
    
    print("Connected to MongoDB")

except Exception as e:
    print(f"Could not connect to MongoDB: {e}")