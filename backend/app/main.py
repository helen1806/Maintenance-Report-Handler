from fastapi import FastAPI, UploadFile, File
from typing import List
from app.services.text_extraction import text_extraction
from app.services.llm_extraction import llm_extractor
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

app = FastAPI()


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):

    results = []

    for file in files:
        print(file.filename) #to be inserted

        text = await text_extraction(file)
        structured_data = await llm_extractor(text)
        results.append(structured_data)
        



    return {
        "message": "Files uploaded successfully",
        "data": results
    }