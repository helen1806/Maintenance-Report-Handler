from pathlib import Path
from fastapi import UploadFile
import pymupdf
import pymupdf4llm
from app.services.llm_extraction import llm_extractor


async def text_extraction(file: UploadFile) -> str:

    extension = Path(file.filename).suffix.lower()

    if extension == ".pdf":
        return await extract_pdf(file)

    else:
        raise ValueError(f"Unsupported file type: {extension}")

async def extract_pdf(file: UploadFile):
    pdf_bytes = await file.read() ##read the bytes and upload

    doc = pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    text = pymupdf4llm.to_markdown(doc)

    return text