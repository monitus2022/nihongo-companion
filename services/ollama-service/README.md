# Ollama Service

This service provides an interface to interact with the Ollama API, allowing users to generate text based on prompts.

## Installation

Locally create conda environment:

```bash
conda create -p env python=3.12
conda activate ./env
pip install -r requirements.txt
```

We are using ollama official library and its python API to interact with the Ollama service. 
- [https://ollama.com/search](https://ollama.com/search)
- [https://github.com/ollama/ollama-python](https://github.com/ollama/ollama-python)

We are not using the official docker image for Ollama to allow for more flexibility in configuration and to avoid issues with the official image.
