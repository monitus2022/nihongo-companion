import uvicorn
from routers.main_router import app
from ollama_prompt_handler import OllamaPromptHandler

ollama_handler = OllamaPromptHandler("gemma3")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    