from pathlib import Path

from app.models.maintenance_schema import MaintenanceExtraction
from app.config import client


async def llm_extractor(document_text: str):

    # Load the prompt template
    prompt_path = Path("app/prompts/firstprompt.txt")
    prompt = prompt_path.read_text(encoding="utf-8")

    # Insert the extracted document
    prompt = prompt.replace("{document_text}", document_text) ##takes in the prompt

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
    