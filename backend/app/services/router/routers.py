def get_routes():
    from semantic_router import Route
    
    general = Route(
        name="General",
        utterances=[
            "What is maintenance?",
            "What is preventive maintenance?",
            "Why does rust occur?",
            "What causes corrosion?",
            "What is a water junction?",
            "How does a valve fail?",
            "Why do drains get clogged?",
            "Explain predictive maintenance.",
        ],
    )
    
    chitchat = Route(
        name="ChitChat",
        utterances=[
            "Hi",
            "Hello",
            "Hey",
            "Good morning",
            "Good afternoon",
            "Good evening",
            "How are you?",
            "Nice to meet you.",
        ],
    )
    
    help_route = Route(
        name="Help",
        utterances=[
            "What can you do?",
            "How do I use this application?",
            "Can I upload a PDF?",
            "How do I ask questions?",
            "What kind of files do you support?",
        ],
    )
    
    graph = Route(
        name="Graph",
        utterances=[
            "Show maintenance reports for Pump A.",
            "What caused the bearing failure?",
            "Find reports about overheating.",
            "List maintenance actions for Valve 3.",
            "Which assets experienced corrosion?",
            "Show reports mentioning leakage.",
        ],
    )
    
    return [general, chitchat, help_route, graph]
