from app.services.router.encoder import get_encoder
from app.services.router.routers import chitchat, general, graph, help_route
from semantic_router import SemanticRouter

# Combine all routes into a list
routes = [general, chitchat, help_route, graph]

_route_layer_instance = None

def get_route_layer() -> SemanticRouter:
    global _route_layer_instance
    if _route_layer_instance is None:
        print("Initializing Semantic Router (lazy load)...")
        _route_layer_instance = SemanticRouter(
            encoder=get_encoder(),
            routes=routes,
            auto_sync="local"
        )
    return _route_layer_instance

if __name__ == "__main__":
    print("--- Testing Semantic Router ---")

    test_questions = [
        "Hello there!",
        "What is a water junction?",
        "Show me the maintenance report for Pump A.",
        "How do I upload a PDF?",
        "Tell me a joke.",  # An out-of-scope question
    ]

    for q in test_questions:
        # Calling the router with a string returns a Route object
        result = route_layer(q)
        print(f"Question: '{q}'\nRouted to: -> [{result.name}]\n")
