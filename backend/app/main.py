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
from app.services.intelligence.similarity_engine import SimilarityEngine
from app.services.intelligence.analytics_engine import AnalyticsEngine
from celery.result import AsyncResult
from fastapi.responses import StreamingResponse

from app.services.text_extraction import text_extraction
from app.services.llm_extraction import llm_extractor
from app.services.graph_builder import GraphBuilder
from app.services.neo4jservice import Neo4jService 
from app.services.qa_service import ask_question
from app.services.graph_chain import mark_graph_changed
from app.services.ontology_mapper import JSONOntologyProvider, OntologyMapper
from app.services.worker_tasks import process_maintenance_report

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
    async with semaphore:
        try:
            if not file.filename.lower().endswith(".pdf"):
                return {"filename": file.filename, "status": "failed", "error": "Invalid file type."}
            
            file_bytes = await file.read()
            file_hash = hashlib.sha256(file_bytes).hexdigest()
            
            # Save the file temporarily so the background worker can read it
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_uploads")
            os.makedirs(temp_dir, exist_ok=True)
            
            temp_file_path = os.path.join(temp_dir, f"{file_hash}.pdf")
            with open(temp_file_path, "wb") as f:
                f.write(file_bytes)
                
            # Dispatch the background task!
            task = process_maintenance_report.delay(
                file_path=temp_file_path,
                filename=file.filename,
                file_hash=file_hash
            )
            
            return {
                "filename": file.filename, 
                "status": "queued", 
                "job_id": task.id
            }

        except Exception as e:
            print(f"Error queuing {file.filename}: {e}")
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
    # We can increase the semaphore since queuing is instant!
    semaphore = asyncio.Semaphore(10) 

    tasks = [process_single_file(file, semaphore) for file in files]
    results = await asyncio.gather(*tasks)
    
    queued = [r for r in results if r["status"] == "queued"]
    failed = [r for r in results if r["status"] == "failed"]
    
    return {
        "message": "File processing complete",
        "summary": {
            "total": len(files),
            "successful": len(queued), # We map queued to successful so the React frontend doesn't break yet!
            "failed": len(failed),
            "skipped": 0
        },
        "jobs": results
    }
# --- Intelligence Layer Endpoints ---

class SimilarityRequest(BaseModel):
    failure_text: str
    top_k: int = 3

@app.post("/api/intelligence/similarity")
def get_similar_failures(request: SimilarityRequest):
    engine = SimilarityEngine()
    results = engine.search_similar_failures(request.failure_text, request.top_k)
    return {"results": results}

@app.get("/api/intelligence/analytics/patterns")
def get_failure_patterns():
    engine = AnalyticsEngine()
    return {"patterns": engine.get_asset_failure_patterns()}

@app.get("/api/intelligence/analytics/reliability")
def get_reliability_scores():
    engine = AnalyticsEngine()
    return {"scores": engine.get_asset_reliability_scores()}
@app.get("/api/jobs/{job_id}/status")
async def job_status_stream(job_id: str):
    """
    Server-Sent Events (SSE) endpoint to stream real-time Celery job status.
    """
    async def event_generator():
        while True:
            # Check the status of the background task
            task = AsyncResult(job_id)
            state = task.state
            
            # SSE protocol requires sending data in this exact format: "data: {...}\n\n"
            yield f"data: {{\"status\": \"{state}\", \"job_id\": \"{job_id}\"}}\n\n"
            
            # Stop streaming if the task is finished
            if state in ["SUCCESS", "FAILURE", "REVOKED"]:
                break
                
            # Wait 1 second before checking again
            await asyncio.sleep(1)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
