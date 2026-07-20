from dotenv import load_dotenv, find_dotenv
from openai import AsyncOpenAI
import os

load_dotenv(find_dotenv())

client = AsyncOpenAI(api_key=os.environ.get("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

DATABASE_URI = os.getenv("DATABASE_URI")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
