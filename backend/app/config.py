from dotenv import load_dotenv, find_dotenv
from google import genai
import os

load_dotenv(find_dotenv())

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

DATABASE_URI = os.getenv("DATABASE_URI")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")