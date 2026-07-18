from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from contextlib import asynccontextmanager

from app.services.text_extraction import text_extraction
from app.services.llm_extraction import llm_extractor
from app.services.graph_builder import GraphBuilder
from app.services.neo4jservice import Neo4jService 
from app.services.qa_service import ask_question
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

# Add CORS middleware to allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace "*" with your React app's URL (e.g. "http://localhost:3000")
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def process_single_file(file: UploadFile):
    
    print(file.filename) 
    text = await text_extraction(file)
    structured_data = await llm_extractor(text)
    standardized_data = mapper.map_extraction(structured_data)
    graph = GraphBuilder().build_graph(standardized_data)
    Neo4jService().save_graph(graph)

    return standardized_data

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    debug: Optional[Dict[str, Any]] = None

@app.post("/ask", response_model=AskResponse)
async def ask_graph_question(request: AskRequest):
    result = ask_question(request.question)
    return AskResponse(**result)

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):

    results = []

    for file in files:
        results.append(await process_single_file(file))
        

    return {
        "message": "Files uploaded successfully",
        "data": results
    }