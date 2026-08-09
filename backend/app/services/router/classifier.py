import os
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

ROUTE_PROMPT = """Classify the following user question into exactly ONE of these four categories:
- "ChitChat": Simple greetings like hi, hello, how are you.
- "Help": Questions asking how to use the app or what it does.
- "General": General knowledge questions about engineering, rust, pumps, etc.
- "Graph": Specific questions about maintenance reports, assets, failure causes, or anything requiring a database search.

User Question: {question}

Respond ONLY with the exact category name (ChitChat, Help, General, or Graph) and nothing else.
"""

def classify(question: str) -> str:
    """
    Takes a user question and returns the name of the route (intent).
    """
    try:
        llm = ChatOpenAI(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            temperature=0,
        )
        prompt = PromptTemplate(
            template=ROUTE_PROMPT, input_variables=["question"]
        )
        chain = prompt | llm
        
        result = chain.invoke({"question": question})
        category = result.content.strip()
        
        if category in ["ChitChat", "Help", "General", "Graph"]:
            return category
        else:
            return "General"
            
    except Exception as e:
        logger.error(f"Error in LLM classification: {e}")
        return "General"
