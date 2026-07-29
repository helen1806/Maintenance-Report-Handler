import os
import logging
from typing import Dict, Any

from fastapi import HTTPException
from neo4j.exceptions import Neo4jError
from app.services.router.classifier import classify

try:
    import openai
except ImportError:
    openai = type("DummyOpenAI", (), {"APIError": type("DummyAPIError", (Exception,), {})})

from app.services.graph_chain import get_graph_qa_chain
from app.services.context_rewriter import rewrite_question_with_context, ChatMessage
from typing import List

logger = logging.getLogger(__name__)

def ask_question(question: str, history: List[ChatMessage] = None) -> Dict[str, Any]:
    """
    Executes a natural language question against the Neo4j graph using LangChain.
    Returns the final answer and conditionally raw debug info based on the DEBUG env var.
    """
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if history is None:
        history = []

    try:
        # 1. Rewrite the question based on conversational history if necessary
        rewritten_question = rewrite_question_with_context(question, history)

        # 1.5 Classify the intent of the question
        route_name = classify(rewritten_question)
        logger.info(f"Question routed to: {route_name}")

        # Handle the non-database routes immediately to save time and API costs!
        if route_name in ["ChitChat", "General"]:
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(
                model="llama-3.3-70b-versatile",
                api_key=os.getenv("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
                temperature=0.5
            )
            
            if route_name == "ChitChat":
                prompt = f"You are a friendly AI assistant for a maintenance application. Briefly respond to this conversational user message: '{rewritten_question}'"
            else:
                prompt = f"You are a helpful AI assistant. Concisely answer this general knowledge question: '{rewritten_question}'"
                
            response = llm.invoke(prompt)
            return {"answer": response.content}
            
        elif route_name == "Help":
            return {"answer": "I can help you analyze maintenance reports, find connected assets, and identify causes of equipment failure! Try asking me to show reports for a specific pump."}
        
        # 2. If route_name == "Graph" (or anything else), proceed to query Neo4j
        chain = get_graph_qa_chain()
        
        # 3. Invoke the chain with the standalone rewritten question
        response = chain.invoke({"query": rewritten_question})

        final_answer = response.get("result", "I'm sorry, I couldn't find an answer to that.")
        intermediate_steps = response.get("intermediate_steps", [])

        # Extract Cypher query and context from intermediate steps
        cypher_query = None
        raw_results = None
        if len(intermediate_steps) >= 1:
            cypher_query = intermediate_steps[0].get("query", "")
        if len(intermediate_steps) >= 2:
            raw_results = intermediate_steps[1].get("context", [])

        is_debug = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

        result_payload = {"answer": final_answer}

        if is_debug:
            result_payload["debug"] = {
                "generated_cypher": cypher_query,
                "raw_results": raw_results
            }

        return result_payload

    except Neo4jError as e:
        logger.error(f"Neo4j Database Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection or query execution failed.")
    
    except openai.APIError as e:
        logger.error(f"Groq API Error: {str(e)}")
        raise HTTPException(status_code=502, detail="Failed to communicate with the Groq AI language model.")
        
    except ValueError as e:
        # LangChain often throws ValueErrors for parsing issues or missing prompt variables
        logger.error(f"LangChain/Validation Error: {str(e)}")
        raise HTTPException(status_code=422, detail="Failed to process the question structure or generate valid Cypher.")
        
    except Exception as e:
        # Generic fallback for unforeseen issues
        logger.error(f"Unexpected Error in qa_service: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while generating the answer.")
