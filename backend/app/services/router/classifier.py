import logging
from app.services.router.semantic_router_service import get_route_layer

logger = logging.getLogger(__name__)

def classify(question: str) -> str:
    """
    Takes a user question and returns the name of the route (intent).
    Hides the underlying semantic-router implementation from the rest of the application.
    """
    try:
        # Get the lazy-loaded router instance
        route_layer = get_route_layer()
        # The semantic router returns a Route object
        result = route_layer(question)
        
        # result.name will be one of our defined routes (e.g., "Graph", "General", "ChitChat")
        # If the question is completely out of scope, result.name might be None, so we provide a fallback.
        if result and result.name:
            return result.name
        else:
            logger.warning(f"No confident route matched for: '{question}'. Defaulting to 'General'.")
            return "General"
            
    except Exception as e:
        logger.error(f"Error in semantic router classification: {e}")
        # Fail gracefully so the application doesn't crash
        return "General"
