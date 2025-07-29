from ollama import ChatResponse, chat

class OllamaPromptHandler:
    """
    Handles prompts for the Ollama model, to serve API requests.
    This class manages the model name, admin prompt, and user prompt.
    """
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.admin_prompt = {
            "role": "system",
            "content": ""
        }
        self.user_prompt = {
            "role": "user",
            "content": ""
        }
        
    @classmethod
    def set_model_name(cls, model_name: str):
        cls.model_name = model_name
    
    @classmethod
    def update_admin_prompt(cls, prompt: str):
        cls.admin_prompt['content'] = prompt

    @classmethod
    def update_user_prompt(cls, prompt: str):
        cls.user_prompt['content'] = prompt

    @classmethod
    def create_chat_session(cls):
        response: ChatResponse = chat(model=cls.model_name, messages=[
            cls.admin_prompt,
            cls.user_prompt
        ])
        return response

    def generate_response(self, prompt: str) -> str:
        # Placeholder for actual response generation logic
        return f"Response from {self.model_name}: {prompt}"
    