from fastapi import FastAPI, UploadFile, File
from typing import List
import os
from contextlib import asynccontextmanager

from app.services.text_extraction import text_extraction
from app.services.llm_extraction import llm_extractor
from app.services.graph_builder import GraphBuilder
from app.services.ontology_mapper import JSONOntologyProvider, OntologyMapper
from dotenv import load_dotenv, find_dotenv 

load_dotenv(find_dotenv())

mapper: OntologyMapper = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mapper
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ontology_dir = os.path.join(base_dir, "ontology")
    
    provider = JSONOntologyProvider(ontology_dir)
    mapper = OntologyMapper(provider)
    yield
    # Cleanup here if needed

app = FastAPI(lifespan=lifespan)

async def process_single_file(file: UploadFile):
    
    print(file.filename) 
    text = await text_extraction(file)
    structured_data = await llm_extractor(text)
    standardized_data = mapper.map_extraction(structured_data)
    graph_received=GraphBuilder.build_graph(standardized_data)
    

    return standardized_data

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):

    results = []

    for file in files:
        results.append(await process_single_file(file))
        

    return {
        "message": "Files uploaded successfully",
        "data": results
    }