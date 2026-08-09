import asyncio
import os
from celery.utils.log import get_task_logger

from app.celery_app import celery_app
from app.services.text_extraction import _parse_pdf_sync
from app.services.llm_extraction import llm_extractor
from app.services.ontology_mapper import OntologyMapper, JSONOntologyProvider
from app.services.graph_builder import GraphBuilder
from app.services.neo4jservice import Neo4jService

logger = get_task_logger(__name__)

def run_async(coro):
    """Helper to run async functions inside a synchronous Celery task"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

@celery_app.task(bind=True)
def process_maintenance_report(self, file_path: str, filename: str, file_hash: str):
    logger.info(f"Starting background extraction for {filename}")
    
    try:
        # 1. Text Extraction
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
        text = _parse_pdf_sync(pdf_bytes)
        
        # 2. LLM Extraction (Async Groq Call)
        structured_data = run_async(llm_extractor(text))
        
        # 3. Ontology Mapping
        # Get the absolute path to the ontology folder
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ontology_dir = os.path.join(base_dir, "ontology")
        mapper = OntologyMapper(JSONOntologyProvider(ontology_dir))
        
        standardized_data = mapper.map_extraction(structured_data)
        
        if not standardized_data.extractions:
            logger.info(f"Skipped {filename} - No data found")
            return {"status": "skipped", "message": "No maintenance data found"}
            
        # 4. Graph Building
        graph = GraphBuilder().build_graph(standardized_data, filename, file_hash)
        
        # 5. Save to Neo4j
        neo4j_service = Neo4jService()
        neo4j_service.save_graph(graph)
        
        # Clean up the temporary file we created for the worker
        if os.path.exists(file_path):
            os.remove(file_path)
            
        logger.info(f"Successfully processed {filename}")
        return {"status": "success", "filename": filename}
        
    except Exception as e:
        logger.error(f"Error processing {filename}: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise e
