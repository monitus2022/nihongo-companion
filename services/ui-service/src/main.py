import gradio as gr
from typing import Optional
import requests
from text_to_speech import TextToSpeechHandler
from pprint import pprint

def prompt_model_with_audio(model_name, user_prompt, admin_prompt: Optional[str] = None)-> str:
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
    text_response = response.json().get("message") if response.status_code == 200 else "Error: Unable to get response from model"

    tts = TextToSpeechHandler()
    tts.set_voice_model(0)
    pprint(tts.list_styles())
    tts.set_voice_style(0)
    tts.synthesize(text=text_response)
    tts.write_wav_to_file(filename="output.wav")

    return text_response, "./media/output.wav"


demo = gr.Interface(
    fn=prompt_model_with_audio,
    inputs=[
        gr.Textbox(label="Model Name", value="gemma3", placeholder="Enter model name"),
        gr.Textbox(label="User Prompt", placeholder="Enter your prompt here"),
        gr.Textbox(label="Admin Prompt (Optional)", placeholder="Optional admin guidance")
    ],
    outputs=[
        gr.Textbox(label="Model Response"),
        gr.Audio(
            label="Generated Speech", 
            type="filepath",
            autoplay=True
            )
    ],
    title="Ollama Model Prompt Interface with TTS",
    description="Enter your prompt to get both text and audio response from the Ollama model."
)

if __name__ == "__main__":
    demo.title = "Ollama Model Prompt Interface"
    demo.description = "Enter the model name, your prompt, and an optional admin prompt to get a response from the Ollama model."
    demo.launch(share=False)
