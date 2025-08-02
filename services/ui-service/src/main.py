import gradio as gr
from typing import Optional
import requests

def prompt_model(model_name, user_prompt, admin_prompt: Optional[str] = None)-> str:
    """
    Function to handle the model prompt.
    
    Args:
        model_name (str): The name of the model to use.
        user_prompt (str): The user's prompt to the model.
        admin_prompt (str): An optional admin prompt to guide the model's response.
        
    Returns:
        str: The response from the model.
    """

    response = requests.post(
        "http://localhost:8000/ollama/prompt",
        json={
            "model": model_name,
            "user_prompt": user_prompt,
            "admin_prompt": admin_prompt if admin_prompt else None,
            "kwargs": {}
        }
    )
    return response.json().get("message") if response.status_code == 200 else "Error: Unable to get response from model"

demo = gr.Interface(
    fn=prompt_model,
    inputs=["text", "text", "text"],
    outputs=["text"],
)

if __name__ == "__main__":
    demo.title = "Ollama Model Prompt Interface"
    demo.description = "Enter the model name, your prompt, and an optional admin prompt to get a response from the Ollama model."
    demo.launch(share=False)

