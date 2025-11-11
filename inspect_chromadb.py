import chromadb
from app.config import settings

# Connect to your existing database
client = chromadb.PersistentClient(path=settings.chroma_persist_dir)

# List all collections
collections = client.list_collections()
print(f"Total collections: {len(collections)}")
for collection in collections:
    print(f"  - {collection.name}")

# Get the resumes collection
try:
    collection = client.get_collection("resumes")
    
    # Get all data from the collection
    data = collection.get()
    
    print(f"\nResumes collection stats:")
    print(f"  Total documents: {len(data['ids'])}")
    print(f"\n{'='*60}")
    
    # Display each resume
    for i in range(len(data['ids'])):
        print(f"\nResume {i+1}:")
        print(f"ID: {data['ids'][i]}")
        print(f"Document: {data['documents'][i][:100]}...")  # First 100 chars
        print(f"Metadata: {data['metadatas'][i]}")
        print(f"Embedding dimension: {len(data['embeddings'][i]) if data['embeddings'] else 'Not included'}")
        print(f"{'-'*60}")
        
except ValueError:
    print("\n'resumes' collection does not exist yet")
