from pathlib import Path
from fastapi import UploadFile
import pymupdf
import pymupdf4llm
from app.services.llm_extraction import llm_extractor
import asyncio


async def text_extraction(file: UploadFile) -> str:

    extension = Path(file.filename).suffix.lower()

    if extension == ".pdf":
        return await extract_pdf(file)

    else:
        raise ValueError(f"Unsupported file type: {extension}")

def _parse_pdf_sync(pdf_bytes: bytes) -> str:
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    return pymupdf4llm.to_markdown(doc)

async def extract_pdf(file: UploadFile):
    pdf_bytes = await file.read() 
    
    # Run the heavy CPU bound task in a separate thread so it doesn't block the FastAPI event loop
    text = await asyncio.to_thread(_parse_pdf_sync, pdf_bytes)

    return text