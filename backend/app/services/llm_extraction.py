import json
from pathlib import Path

from app.models.maintenance_schema import MaintenanceExtraction
from app.config import client

prompt_path = Path("app/prompts/firstprompt.txt")
async def llm_extractor(document_text: str):

    
    prompt = prompt_path.read_text(encoding="utf-8")

    # Insert the extracted document
    prompt = prompt.replace("{document_text}", document_text) 

    # Ensure the prompt asks for JSON and provide the exact schema
    schema_str = json.dumps(MaintenanceExtraction.model_json_schema(), indent=2)
    prompt = prompt + f"\n\nRespond ONLY with a valid JSON object matching exactly this JSON Schema:\n{schema_str}"

    # Send prompt to Groq via OpenAI compatible API
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content
    return MaintenanceExtraction.model_validate_json(content)
    