from pydantic_settings import BaseSettings
import chromadb

class Settings(BaseSettings):
    openai_api_key: str
    chroma_persist_dir: str = "./data/chromadb"
    
    class Config:
        env_file = ".env"

settings = Settings()

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)