import os
from dotenv import load_dotenv

from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI

from app.prompts.cypher_prompt import CUSTOM_CYPHER_PROMPT

# Load environment variables
load_dotenv()

# Singleton instance cache
_qa_chain_instance = None
_graph_changed = False

def mark_graph_changed():
    """
    Flags that the underlying Neo4j graph has been modified (e.g., via upload).
    This forces a complete rebuild of the Neo4jGraph and QA Chain on the next query.
    """
    global _graph_changed
    _graph_changed = True

def get_graph_qa_chain() -> GraphCypherQAChain:
    """
    Initializes and returns a singleton instance of the GraphCypherQAChain.
    Connects to Neo4j, sets up the Groq LLM, and injects the custom Cypher prompt.
    Rebuilds the chain from scratch if the graph schema was modified.
    """
    global _qa_chain_instance, _graph_changed
    
    if _qa_chain_instance is not None:
        if not _graph_changed:
            return _qa_chain_instance
        else:
            # We are about to rebuild the chain. To prevent database connection leaks, 
            # we must explicitly close the old Neo4j driver before discarding the object.
            try:
                if hasattr(_qa_chain_instance, "graph") and hasattr(_qa_chain_instance.graph, "_driver"):
                    _qa_chain_instance.graph._driver.close()
            except Exception:
                pass

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
    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        temperature=0
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

    # Reset the dirty flag now that we've rebuilt the chain with the fresh schema
    _graph_changed = False

    return _qa_chain_instance
