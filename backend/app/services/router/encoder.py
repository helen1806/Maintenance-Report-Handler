_encoder_instance = None

def get_encoder():
    global _encoder_instance
    if _encoder_instance is None:
        from semantic_router.encoders import HuggingFaceEncoder
        print("Loading HuggingFace model into RAM (lazy load)...")
        _encoder_instance = HuggingFaceEncoder(name="BAAI/bge-small-en-v1.5")
    return _encoder_instance
