from fastapi import FastAPI, HTTPException
import requests

def main():
    app = FastAPI()

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app