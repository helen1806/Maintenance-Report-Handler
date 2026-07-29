from app.services.router.encoder import encoder
from app.services.router.routers import chitchat, general, graph, help_route
from semantic_router import SemanticRouter

# Combine all routes into a list
routes = [general, chitchat, help_route, graph]

# Create the RouteLayer (which acts as our SemanticRouter)
route_layer = SemanticRouter(
    encoder=encoder,
    routes=routes,
    auto_sync="local"
)

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
