import pdfplumber
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, BackgroundTasks
from app.config import resumes_collection
from datetime import datetime
from typing import Dict

from app.routes.auth import get_user_id
from app.agents.tools import find_and_match_jobs
from app.agents.graph import app as agent_graph

router = APIRouter()

@router.get("/resume-status")
async def get_resume_status(user_id: str = Depends(get_user_id)):
    resume = resumes_collection.find_one(
        {"user_id": user_id},
        sort=[("uploaded_at", -1)] 
    )

    if not resume:
        raise HTTPException(status_code=404, detail="No resume found")

    return {
        "filename": resume.get("filename"),
        "status": resume.get("status", "pending"),
        "matches": resume.get("matches", []),
        "research": resume.get("research", {}),
        "uploaded_at": resume.get("uploaded_at")
    }

@router.post("/upload-resume")
async def upload_resume(background_tasks: BackgroundTasks, file: UploadFile = File(...), user_id: str = Depends(get_user_id)) -> Dict:
    # validate file
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pdf files are allowed")

    try:
        file_content = await file.read()
        text_content = read_pdf_plumber(file_content)

        resume_data = {
            "user_id": user_id,
            "filename": file.filename,
            "content": text_content,
            "uploaded_at": datetime.utcnow(),
            "content_type": file.content_type,
            "status": "pending", 
            "matches": []
        }

        result = resumes_collection.insert_one(resume_data)
        resume_id = result.inserted_id

        background_tasks.add_task(process_resume_background, user_id, text_content, resume_id)

        return {
            "message": "Resume uploaded successfully",
            "id": str(result.inserted_id),
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error while reading pdf: {str(e)}")

def read_pdf_plumber(file_bytes):
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

async def process_resume_background(user_id: str, resume_text: str, resume_id: str):
    print(f"Starting ai analysis for user {user_id}...")
    
    try:
        resumes_collection.update_one(
            {"_id": resume_id}, 
            {"$set": {"status": "processing"}}
        )

        initial_state = {"resume_text": resume_text}

        # invoke graph
        final_state = await agent_graph.ainvoke(initial_state)

        matches = final_state.get("matches", [])

        research_notes = final_state.get("research_notes", {})
        print(f"Graph Finished. Research collected for: {list(research_notes.keys())}")
        
        # Save the actual results to MongoDB
        resumes_collection.update_one(
            {"_id": resume_id}, 
            {
                "$set": {
                    "status": "completed", 
                    "matches": matches,
                    "research": research_notes,
                    "completed_at": datetime.utcnow()
                }
            }
        )
        print(f"AI Agent finished for user {user_id}")

    except Exception as e:
        print(f"ERROR in Background Task: {e}")
        # Save failure results so frontend stops spinning
        resumes_collection.update_one(
            {"_id": resume_id}, 
            {"$set": {"status": "failed", "error": str(e)}}
        )