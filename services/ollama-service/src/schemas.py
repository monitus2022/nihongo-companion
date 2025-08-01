from pydantic import BaseModel, Field
from typing import Optional
from config import DEFAULT_MODEL

class OllamaRequestBody(BaseModel):
    """
    Represents a prompt to be sent to the Ollama model.
    """
    model: str = Field(DEFAULT_MODEL, description="The name of the Ollama model to use.")
    user_prompt: str = Field(..., description="The user's prompt to the model.")
    admin_prompt: Optional[str] = Field(None, description="An optional admin prompt to guide the model's response.")
    kwargs: Optional[dict] = Field(None, description="Additional keyword arguments for the model request.")
    

class OllamaResponseBody(BaseModel):
    """
    Represents the response from the Ollama model.
    """
    model: str = Field(..., description="The model used to generate the response.")
    user_prompt: str = Field(..., description="The user's prompt that was sent to the model.")
    admin_prompt: Optional[str] = Field(None, description="The admin prompt used to guide the model's response, if any.")
    message: str = Field(..., description="The message content returned by the model.") 
    total_duration: Optional[float] = Field(None, description="The total duration of the request in seconds.")
    timestamp: str = Field(..., description="The timestamp of the response.")