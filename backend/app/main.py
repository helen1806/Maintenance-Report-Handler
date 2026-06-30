from fastapi import FastAPI, UploadFile, File
from typing import List
from app.services import text_extraction,llm_extraction

app = FastAPI()


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):

    extracted_texts = []

    for file in files:
        print(file.filename)

        text = await text_extraction(file)
        structured_data = await llm_extraction(text)

    return {
        "message": "Files uploaded successfully",
        "uploaded_files": len(files),
        "documents_processed": len(extracted_texts)
    }