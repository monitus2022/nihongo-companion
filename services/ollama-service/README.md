# Ollama Service

This service provides an interface to interact with the Ollama API, allowing users to generate text based on prompts.

## Installation

Make sure you have ollama running in the background. For installation:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```
To start ollama in the background:
```bash
ollama serve
```

Locally create conda environment:

```bash
conda create -p env python=3.12
conda activate ./env
pip install -r requirements.txt
```

We are using ollama official library and its python API to interact with the Ollama service. 
- [https://ollama.com/search](https://ollama.com/search)
- [https://github.com/ollama/ollama-python](https://github.com/ollama/ollama-python)
