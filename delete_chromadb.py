import chromadb
from app.config import settings

# Connect to ChromaDB (adjust for PersistentClient or HttpClient as needed)
client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
collection = client.get_collection(name="resumes")

# # Delete a document by its ID (string or list)
# doc_id = "043bd98e-3bb0-42c6-9434-c4fd011c4f5c_proj_0"  # e.g., 'abc123_full' or a list of IDs
# collection.delete(ids=doc_id)  # Can provide a single string or a list

# print(f"Deleted document ID(s): {doc_id}")

## delete all chunks from resume
resume_id = "043bd98e-3bb0-42c6-9434-c4fd011c4f5c"  # e.g., 'a1b2c3...'
# Retrieve all IDs linked to that resume_id
results = collection.get(where={"resume_id": resume_id})
ids_to_delete = results["ids"]

if ids_to_delete:
    collection.delete(ids=ids_to_delete)
    print(f"Deleted all chunks for resume_id: {resume_id}")
else:
    print("No chunks found for given resume_id.")

## delete all collections
# collection.delete()
# print("All documents in collection deleted.")

