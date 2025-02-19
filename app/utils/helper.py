import os
from fastapi import UploadFile
import pymupdf4llm
import mammoth


async def save_upload_file(uploaded_file: UploadFile, folder_path: str = "./temp") -> str:
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, uploaded_file.filename)
    with open(file_path, "wb") as f:
        f.write(await uploaded_file.read())

    return file_path

def delete_file(file_path: str) -> bool: 
    if os.path.exists(file_path):
        os.remove(file_path)


def convert_pdf_to_md(file_path: str) -> str:
    md_text = pymupdf4llm.to_markdown(file_path)
    return md_text

def convert_docx_to_md(file_path: str) -> str:
    with open(file_path, "rb") as docx_file:
        result = mammoth.convert_to_markdown(docx_file)
    return result.value