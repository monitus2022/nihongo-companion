from fastapi import APIRouter

query_router = APIRouter()

@query_router.get("/{model_name}")
def query_ollama_model(model_name: str):
    return {"model_name": model_name, "response": "This is a placeholder response."}
