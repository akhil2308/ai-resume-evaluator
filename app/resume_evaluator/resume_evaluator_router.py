from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile

from app.settings import ALLOWED_EXTENSIONS, MAX_FILES
from app.resume_evaluator.resume_evaluator_service import extract_criteria_service, score_resumes_service, create_excel_from_result

import logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/extract-criteria")
async def extract_criteria(file: UploadFile = File(...)):
    try:
        ext = file.filename.split(".")[-1]
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX are allowed.")

        criteria = await extract_criteria_service(file, ext)
        return {
            "criteria": criteria
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@router.post("/score-resumes")
async def score_resumes(
    files: List[UploadFile] = File(...),
    criteria: str = Form(...),
    download: bool = Form(False)
    ):
    try:
        # Check max number of uploaded files
        if len(files) > MAX_FILES:
            raise HTTPException(status_code=400, detail=f"Max number of files allowed is {MAX_FILES}")
        
        # Check file extensions
        for file in files:
            file_extension = file.filename.split('.')[-1]
            if file_extension.lower() not in ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX are allowed.")
        
        result = await score_resumes_service(files, criteria)
        
        # Return an Excel file if download is true, otherwise return JSON
        if download:
            return create_excel_from_result(result)
        else:
            return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")