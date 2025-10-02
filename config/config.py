CONFIG = {
    "text": {
        "provider": "openai",  # "local" or "openai"
        "model": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "api_key": "YOUR_OPENROUTER_API_KEY_HERE"
        
        # For local usage, change to:
        # "provider": "local",
        # "model": "deepseek-r1-distill-qwen-7b", 
        # "url": "http://localhost:1234/v1/chat/completions"
        # "api_key": None
    },
    "vision": {
        # Vision is local
        "model": "google/gemma-3-4b",
        "url": "http://localhost:1234/v1/chat/completions"
    },
    "server": {
        "host": "127.0.0.1",
        "port": 5000,
        "debug": True
    }
}