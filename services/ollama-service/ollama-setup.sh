#!/bin/bash

# Failsafe
set -e
# set -x # Uncomment for debugging

echo "Initializing Ollama..."
ollama serve > ollama.log 2>&1 &  # Start Ollama in the background and log output
# Wait for Ollama to be ready by polling its health endpoint
max_retries=20
retry_count=0
until curl -sf http://localhost:11434/; do
    sleep 1
    retry_count=$((retry_count+1))
    if [ "$retry_count" -ge "$max_retries" ]; then
        echo "Ollama failed to start or is not responding on the health endpoint."
        exit 1
    fi
done

# Check if Ollama is running
echo "Setting up Ollama models..."
# Check if Modelfile exists before creating the model
if [ ! -f ./Modelfile ]; then
    echo "Error: Modelfile not found in the current directory."
    exit 1
fi
# Use Modelfile to initialize models
ollama create jp-gemma3 -f ./Modelfile
ollama run jp-gemma3

echo "Ollama setup complete."
# ollama show --modelfile jp-gemma3 # Uncomment to show model details

exec python3 main.py  # Start the FastAPI application
