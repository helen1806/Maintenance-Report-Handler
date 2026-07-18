import os
from dotenv import load_dotenv

from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_google_genai import ChatGoogleGenerativeAI

from app.prompts.cypher_prompt import CUSTOM_CYPHER_PROMPT

# Load environment variables
load_dotenv()

# Singleton instance cache
_qa_chain_instance = None

def get_graph_qa_chain() -> GraphCypherQAChain:
    """
    Initializes and returns a singleton instance of the GraphCypherQAChain.
    Connects to Neo4j, sets up the Gemini LLM, and injects the custom Cypher prompt.
    """
    global _qa_chain_instance
    if _qa_chain_instance is not None:
        return _qa_chain_instance

    # Read configuration for verbosity
    debug_mode = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    verbose_logging = os.getenv("GRAPH_QA_VERBOSE", str(debug_mode)).lower() in ("true", "1", "yes")

    # Initialize Graph connection
    graph = Neo4jGraph(
        url=os.getenv("DATABASE_URI"),
        username=os.getenv("DATABASE_USERNAME"),
        password=os.getenv("DATABASE_PASSWORD"),
        database=os.getenv("DATABASE_USERNAME"), # using the user provided env fallback
        refresh_schema=True,
    )

    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0,
    )

    # Create the Graph QA Chain
    _qa_chain_instance = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=graph,
        verbose=verbose_logging,
        cypher_prompt=CUSTOM_CYPHER_PROMPT,
        allow_dangerous_requests=True,
        return_intermediate_steps=True # Always needed to return raw query/results for DEBUG mode
    )

    return _qa_chain_instance
