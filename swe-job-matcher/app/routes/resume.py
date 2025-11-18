import pdfplumber
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.config import resumes_collection
from datetime import datetime
from typing import Dict

router = APIRouter()

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)) -> Dict:
    # validate file
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pdf files are allowed")

    try:
        file_content = await file.read()
        response = read_pdf_plumber(file_content)

        resume_data = {
            "filename": file.filename,
            "content": response,
            "uploaded_at": datetime.utcnow(),
            "content_type": file.content_type
        }

        result = resumes_collection.insert_one(resume_data)

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