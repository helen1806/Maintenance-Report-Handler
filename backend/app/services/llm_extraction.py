from pathlib import Path

from app.models.maintenance_schema import MaintenanceExtraction
from app.config import client

prompt_path = Path("app/prompts/firstprompt.txt")
async def llm_extractor(document_text: str):

    
    prompt = prompt_path.read_text(encoding="utf-8")

    # Insert the extracted document
    prompt = prompt.replace("{document_text}", document_text) 

    # Send prompt + schema to the LLM
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": MaintenanceExtraction,
        }
    )

    return response.parsed
    