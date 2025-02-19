import os
import json
import pandas as pd
from io import BytesIO
import asyncio
from openai import AsyncOpenAI
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from app.settings import OPENAI_API_KEY, OPENAI_API_MODEL
from app.utils.helper import save_upload_file, delete_file, convert_pdf_to_md, convert_docx_to_md
from app.resume_evaluator.resume_evaluator_config import JOB_DESCRIPTION_SYSTEM_PROMPT, JOB_DESCRIPTION_USER_PROMPT, \
    CRITERIA_SYSTEM_PROMPT, CRITERIA_USER_PROMPT, SCORING_COLUMNS_SYSTEM_PROMPT, SCORING_COLUMNS_USER_PROMPT, \
    RESUME_SCORING_SYSTEM_PROMPT, RESUME_SCORING_USER_PROMPT

import logging
logger = logging.getLogger(__name__)
    
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

def convert_file_to_md(file_path: str, file_extension: str):
    if file_extension == "pdf":
        return convert_pdf_to_md(file_path)
    elif file_extension == "docx":
        return convert_docx_to_md(file_path)
    else:
        raise Exception("Invalid file type. Only PDF and DOCX are allowed.")
    

async def extract_criteria_service(file: UploadFile, file_extension: str):
    """
    Extracts ranking criteria from job description file through 2-step LLM processing:
    
    1. Clean JD Extraction:
       - Converts PDF/DOCX to markdown (optimal for LLM parsing)
       - Removes non-JD content (company info, benefits, etc)
    
    2. Criteria Generation:
       - Extracts requirements from cleaned JD
       - Groups similar requirements
       - Summarizes into distinct criteria
       - Returns JSON with standardized format
    """
    # save the uploaded file
    file_path = await save_upload_file(file)
    logger.info(f"File saved at: {file_path}")
    
    try:
        # convert to markdown
        md_text = convert_file_to_md(file_path, file_extension)
        
        try:
            # extract job description
            logger.info("Extracting job description")
            response = await openai_client.chat.completions.create(
                model=OPENAI_API_MODEL,
                messages=[
                    {"role": "system", "content": JOB_DESCRIPTION_SYSTEM_PROMPT},
                    {"role": "user", "content": JOB_DESCRIPTION_USER_PROMPT.format(content=md_text)},
                ],
                temperature=0.3, # to fill in missing letters (if improperly extracted)
                max_tokens=500,
            )
            job_description = response.choices[0].message.content 
        except Exception as e:
            logger.error(f"Debugging AI error: {e}", exc_info=True)
            raise Exception("Model call failed to extract job description")

        try:
            # extract criteria
            logger.info("Extracting criteria")
            response = await openai_client.chat.completions.create(
                model=OPENAI_API_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": CRITERIA_SYSTEM_PROMPT},
                    {"role": "user", "content": CRITERIA_USER_PROMPT.format(content=job_description)},
                ],
                temperature=0, # to ensure the data is in JSON format 
                max_tokens=500,
            )
            result = response.choices[0].message.content 
            logger.info(f"Extracted criteria: {result}")
        except Exception as e:
            logger.error(f"Debugging AI error: {e}", exc_info=True)
            raise Exception("Model call failed to extract criteria")        
        
        result = json.loads(result)
        return result.get("criteria", result)
    except Exception as e:
        raise e
    finally:
        delete_file(file_path)
        

async def score_resumes_service(files: list[UploadFile], criteria: str):
    """
    Scores multiple resumes against criteria through optimized async pipeline:
    
    1. Column Name Generation:
       - Creates standardized scoring columns from criteria
       - Prevents LLM hallucination in output format
    
    2. Async Resume Processing:
       - Parallel processing of each resume
       - Scores each criterion (0-5) based on explicit evidence
       - Calculates total score server-side (avoiding LLM math errors)

    """
    # save the uploaded files
    file_paths = [await save_upload_file(file) for file in files]
    try:
        # convert to markdown
        md_texts = [convert_file_to_md(file_path, file.filename.split(".")[-1]) for file_path, file in zip(file_paths, files)]
        
        try:
            # extract scoring columns
            logger.info("Extracting scoring columns")
            response = await openai_client.chat.completions.create(
                model=OPENAI_API_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SCORING_COLUMNS_SYSTEM_PROMPT},
                    {"role": "user", "content": SCORING_COLUMNS_USER_PROMPT.format(criteria=criteria)},
                ],
                temperature=0,
                max_tokens=300,
            )
            result = response.choices[0].message.content 
        except Exception as e:
            logger.error(f"Debugging AI error: {e}", exc_info=True)
            raise Exception("Model call failed to score resumes")
        
        result = json.loads(result)
        column_names = result.get("column_names", [])
        if not column_names:
            raise Exception("Model call failed extract column names")
        
        sample_json = {}
        sample_json['Candidate Name'] = "<Candidate Name>"
        for column in column_names:
            sample_json[column] = "<score: int>"
        
        # string representation of the sample json
        columns_str = json.dumps(column_names)
        sample_json_str = json.dumps(sample_json, indent=4)
        
        # Build a list of tasks for scoring each resume concurrently.
        logger.info("Scoring resumes")
        scoring_tasks = []
        for md_text in md_texts:
            task = openai_client.chat.completions.create(
                model=OPENAI_API_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": RESUME_SCORING_SYSTEM_PROMPT.format(columns=columns_str)},
                    {"role": "user", "content": RESUME_SCORING_USER_PROMPT.format(
                        resume_content=md_text,
                        criteria=criteria,
                        sample_json=sample_json_str
                    )},
                ],
                temperature=0,
                max_tokens=500,
            )
            scoring_tasks.append(task)

        # Run all scoring tasks concurrently and wait for responses.
        try:
            logger.info("Waiting for resume scoring responses")
            responses = await asyncio.wait_for(asyncio.gather(*scoring_tasks), timeout=30)
        except asyncio.TimeoutError:
            raise Exception("Timeout while waiting for resume scoring responses.")
        
        # Process responses:
        scored_resumes = []
        for response in responses:
            resume_result = response.choices[0].message.content
            resume_result = json.loads(resume_result)
            scored_resumes.append(resume_result)
        
        # calculate the total score for each resume
        for resume in scored_resumes:
            resume['Total Score'] = sum([score for key, score in resume.items() if isinstance(score, int)])
            
        return scored_resumes
    except Exception as e:
        raise e
    finally:
        for file_path in file_paths:
            delete_file(file_path)
            

def create_excel_from_result(result: list) -> StreamingResponse:
    df = pd.DataFrame(result)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    headers = {
        "Content-Disposition": 'attachment; filename="results.xlsx"'
    }
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )
