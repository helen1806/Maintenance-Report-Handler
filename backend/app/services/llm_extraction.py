from pathlib import Path

from openai import AsyncOpenAI

from app.models.maintenance_schema import MaintenanceExtraction

client = AsyncOpenAI()


async def llm_extractor(document_text: str):

    # Load the prompt template
    prompt_path = Path("app/prompts/firstprompt.txt")
    prompt = prompt_path.read_text(encoding="utf-8")

    # Insert the extracted document
    prompt = prompt.replace("{document_text}", document_text) ##takes in the prompt

    # Send prompt + schema to the LLM
    response = await client.responses.parse(
        model="gpt-5.5",
        input=prompt,
        text_format=MaintenanceExtraction
    )

    return response.output_parsed