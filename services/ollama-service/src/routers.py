from fastapi import APIRouter, HTTPException
from ollama_prompt_handler import OllamaPromptHandler
from schemas import OllamaRequestBody, OllamaResponseBody
from config import DEFAULT_ADMIN_PROMPT, SERVICE_NAME

# Create router instance
router = APIRouter()

# Initialize the Ollama handler
ollama_handler = OllamaPromptHandler()


@router.get("/")
def health_check():
    """
    Health check endpoint to verify service is running.
    
    Returns:
        dict: Service status information
    """
    return {
        "service": SERVICE_NAME,
        "message": "Service is running properly"
    }


@router.post("/prompt", response_model=OllamaResponseBody)
def prompt_ollama(request: OllamaRequestBody):
    """
    Send a prompt to the Ollama model and get a response.
    
    Args:
        request (OllamaRequestBody): The request containing model name and prompts
        
    Returns:
        OllamaResponseBody: The structured response from the Ollama model
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        # Apply default admin prompt if not provided
        if not request.admin_prompt or request.admin_prompt.strip() == "":
            request.admin_prompt = DEFAULT_ADMIN_PROMPT
            
        # Use the callable handler to process the request
        response = ollama_handler(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing Ollama request: {str(e)}"
        )
