from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal
import os
import hashlib
import asyncio
import time
from contextlib import asynccontextmanager

from app.services.text_extraction import text_extraction
from app.services.llm_extraction import llm_extractor
from app.services.graph_builder import GraphBuilder
from app.services.neo4jservice import Neo4jService 
from app.services.qa_service import ask_question
from app.services.graph_chain import mark_graph_changed
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

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit

async def process_single_file(file: UploadFile, semaphore: asyncio.Semaphore):
    start_time = time.time()
    async with semaphore:
        try:
            print(file.filename) 
            
            if not file.filename.lower().endswith(".pdf"):
                return {"filename": file.filename, "status": "failed", "error": "Invalid file type. Only PDFs are accepted."}
            
            file_bytes = await file.read()
            
            if len(file_bytes) > MAX_FILE_SIZE_BYTES:
                return {"filename": file.filename, "status": "failed", "error": f"File size exceeds the {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB limit."}
                
            file_hash = hashlib.sha256(file_bytes).hexdigest()
            await file.seek(0)
            
            neo4j_service = Neo4jService()
            # Offload blocking network call
            exists = await asyncio.to_thread(neo4j_service.report_exists, file_hash)
            if exists:
                return {"filename": file.filename, "status": "skipped", "message": "File already uploaded"}

            text = await text_extraction(file)
            structured_data = await llm_extractor(text)
            standardized_data = mapper.map_extraction(structured_data)
            graph = GraphBuilder().build_graph(standardized_data, file.filename, file_hash)
            
            # Offload blocking network call
            await asyncio.to_thread(neo4j_service.save_graph, graph)
            
            end_time = time.time()
            processing_time = round(end_time - start_time, 2)
            
            report_node = next((n for n in graph.nodes if n.label == "MaintenanceReport"), None)
            report_id = report_node.properties.get("report_id") if report_node else None
            
            extracted_entities_count = sum(1 for v in standardized_data.dict().values() if v is not None)
            
            metadata = {
                "report_id": report_id,
                "filename": file.filename,
                "extracted_entities_count": extracted_entities_count,
                "graph_statistics": {
                    "nodes_created": len(graph.nodes),
                    "relationships_created": len(graph.relationships)
                },
                "processing_time_seconds": processing_time
            }

            return {
                "filename": file.filename, 
                "status": "success", 
                "data": standardized_data.dict(), 
                "metadata": metadata
            }
        except Exception as e:
            print(f"Error processing {file.filename}: {e}")
            return {"filename": file.filename, "status": "failed", "error": str(e)}

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class AskRequest(BaseModel):
    question: str
    history: List[ChatMessage] = []

class AskResponse(BaseModel):
    answer: str
    debug: Optional[Dict[str, Any]] = None

@app.post("/ask", response_model=AskResponse)
async def ask_graph_question(request: AskRequest):
    try:
        # Offload the blocking Graph QA chain (LLM and Neo4j network calls) to a background thread
        result = await asyncio.to_thread(ask_question, request.question, request.history)
        return AskResponse(**result)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "message": "Unable to answer the question.",
                "details": e.detail
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Unable to answer the question.",
                "details": str(e)
            }
        )

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):

    # Limit concurrent extractions to 3 to prevent LLM API rate limits and memory spikes
    semaphore = asyncio.Semaphore(3)

    tasks = [process_single_file(file, semaphore) for file in files]
    results = await asyncio.gather(*tasks)
    
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]
    skipped = [r for r in results if r["status"] == "skipped"]
    
    if len(successful) > 0:
        mark_graph_changed()

    return {
        "message": "File processing complete",
        "summary": {
            "total": len(files),
            "successful": len(successful),
            "failed": len(failed),
            "skipped": len(skipped)
        },
        "successful": successful,
        "failed": failed,
        "skipped": skipped
    }