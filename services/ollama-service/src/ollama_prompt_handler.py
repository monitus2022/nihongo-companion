from ollama import ChatResponse, chat
from schemas import OllamaRequestBody, OllamaResponseBody
from utils import remove_seperators_from_text

class OllamaPromptHandler:
    """
    Handles prompts for the Ollama model, to serve API requests.
    This class manages the model name, admin prompt, and user prompt.
    """
    def __init__(self):
        self.model = ""
        self.admin_prompt = {
            "role": "system",
            "content": ""
        }
        self.user_prompt = {
            "role": "user",
            "content": ""
        }
        
    def _set_model(self, model: str):
        """Sets the Ollama model name to use for chat requests."""
        self.model = model

    def _update_admin_prompt(self, prompt: str):
        """Updates the system prompt that provides context to the model."""
        self.admin_prompt['content'] = prompt

    def _update_user_prompt(self, prompt: str):
        """Updates the user prompt content."""
        self.user_prompt['content'] = prompt

    def _create_chat_session(self):
        """
        Creates a chat session with the configured model and prompts.
        
        Returns:
            ChatResponse: The response from the Ollama chat API.
        """
        response: ChatResponse = chat(model=self.model, messages=[
            self.admin_prompt,
            self.user_prompt
        ])
        return response

    def handle(self, request_body: OllamaRequestBody) -> ChatResponse:
        """
        Handles an incoming request by setting up the model and prompts, then generating a response.
        
        Args:
            request_body (OllamaRequestBody): The request containing model name and prompts.
            
        Returns:
            ChatResponse: Raw response from the Ollama model.
        """
        self._set_model(request_body.model)
        self._update_admin_prompt(request_body.admin_prompt)
        self._update_user_prompt(request_body.user_prompt)

        response: ChatResponse = chat(
            model=self.model,
            messages=[
                self.admin_prompt,
                self.user_prompt
            ]
        )
        return response

    def parse_response(self, response: ChatResponse) -> OllamaResponseBody:
        """
        Parses the raw ChatResponse into a structured OllamaResponseBody.
        
        Extracts timestamp, duration, and message content, cleaning text separators.
        Converts duration from nanoseconds to seconds.
        
        Args:
            response (ChatResponse): Raw response from Ollama chat API.
            
        Returns:
            OllamaResponseBody: Structured response with cleaned content.
        """
        timestamp: str = response.created_at if response.created_at else None
        total_duration: int = response.total_duration if response.total_duration else None
        if total_duration:
            total_duration = round(total_duration / 10**9, 2)  # Convert nanoseconds to seconds
        content: str = response.message.content if response.message else {}
        return OllamaResponseBody(
            model=self.model,
            user_prompt=remove_seperators_from_text(self.user_prompt['content']),
            admin_prompt=remove_seperators_from_text(self.admin_prompt['content']),
            message=remove_seperators_from_text(content),
            total_duration=total_duration,
            timestamp=timestamp
        )
        
    def __call__(self, request_body: OllamaRequestBody) -> OllamaResponseBody:
        """
        Makes the handler callable, providing a complete request-to-response pipeline.
        
        This is the main entry point that orchestrates the entire flow:
        1. Handles the request (sets up model and prompts)
        2. Gets response from Ollama
        3. Parses and structures the response
        
        Args:
            request_body (OllamaRequestBody): The incoming request.
            
        Returns:
            OllamaResponseBody: Complete structured response ready for API return.
        """
        response = self.handle(request_body)
        return self.parse_response(response)
    