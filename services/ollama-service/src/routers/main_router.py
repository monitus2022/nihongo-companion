from fastapi import FastAPI
from .ollama_agent import query_router

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Register the ollama agent route
for r in [
    query_router
    ]:
    app.include_router(r, prefix="/ollama", tags=["ollama"])