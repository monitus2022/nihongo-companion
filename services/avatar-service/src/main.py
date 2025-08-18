import gradio as gr
from typing import Optional, Dict
import requests
from text_to_speech import TextToSpeechHandler
from pprint import pprint
from time import time
import json

# Create single TTS handler instance with voice options loaded
tts = TextToSpeechHandler()

def prompt_model_with_audio(
    model_name, 
    user_prompt,
    admin_prompt,
    voice_actor_name,
    voice_style_name)-> tuple:
    """
    Function to handle the model prompt.
    
    Args:
        model_name (str): The name of the model to use.
        user_prompt (str): The user's prompt to the model.
        admin_prompt (str): An optional admin prompt to guide the model's response.
        voice_actor_name (str): The name of the voice actor.
        voice_style_name (str): The name of the voice style.
        
    Returns:
        tuple: The response from the model and audio file path.
    """
    
    # Convert user-friendly names to IDs using TTS handler
    voice_model_id = tts.get_voice_id_from_name(voice_actor_name)
    voice_style_id = tts.get_style_id_from_name(voice_actor_name, voice_style_name)

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

    tts.set_voice_model(voice_model_id)
    tts.set_voice_style(voice_style_id)

    start_time = time()
    tts.synthesize(text=text_response)

    print(f"Voice synthesis time: {time() - start_time} seconds")
    tts.write_wav_to_file(filename="output.wav")

    return text_response, "./media/output.wav"


with gr.Blocks(title="🎌 Nihongo Companion") as demo:
    gr.Markdown("# 🎌 Nihongo Companion - AI Japanese Tutor")
    
    # Usage instructions paragraph
    gr.Markdown(f"""
    ## 📝 How to Use This Interface
    
    1. **Model Name**: Enter the AI model you want to use (default: gemma3)
    2. **User Prompt**: Type your message or question in Japanese or English
    3. **Admin Prompt**: (Optional) Provide context like "You are a Japanese tutor" to guide the AI's response
    4. **Voice Actor & Style**: Choose the voice characteristics for the audio output
    5. **Click Submit**: The AI will generate both text and audio responses automatically
    
    **Example**: Try asking "こんにちは、元気ですか？" (Hello, how are you?) with admin prompt "You are a friendly Japanese conversation partner."
    """)

    with gr.Row():
        with gr.Column():
            model_name = gr.Textbox(label="Model Name", value="gemma3", placeholder="Enter model name")
            admin_prompt = gr.Textbox(label="Admin Prompt (Optional)", placeholder="Optional admin guidance")
            
            # Dynamic voice selection with safe initialization
            initial_actors = tts.get_voice_choices() or ["Loading..."]
            initial_actor = initial_actors[0]
            initial_styles = tts.get_style_choices(initial_actor) or ["Loading..."]
            
            voice_actor = gr.Dropdown(
                label="Voice Actor", 
                choices=initial_actors, 
                value=initial_actor
            )
            voice_style = gr.Dropdown(
                label="Voice Style", 
                choices=initial_styles,
                value=initial_styles[0]
            )
            
            user_prompt = gr.MultimodalTextbox(label="User Prompt", value="こんにちは、元気ですか？", placeholder="Enter your prompt here")
            submit_btn = gr.Button("Generate Response & Audio", variant="primary")
        
        with gr.Column():
            text_output = gr.Textbox(label="Model Response")
            audio_output = gr.Audio(
                label="Generated Speech", 
                type="filepath",
                autoplay=True
            )
    
    # Update voice style choices when voice actor changes
    def update_voice_styles(voice_actor_name):
        styles = tts.get_style_choices(voice_actor_name)
        return gr.Dropdown(choices=styles, value=styles[0] if styles else "ノーマル")
    
    voice_actor.change(
        fn=update_voice_styles,
        inputs=[voice_actor],
        outputs=[voice_style]
    )
    
    # Handle form submission
    submit_btn.click(
        fn=prompt_model_with_audio,
        inputs=[model_name, user_prompt, admin_prompt, voice_actor, voice_style],
        outputs=[text_output, audio_output]
    )

if __name__ == "__main__":
    # Voice options are already loaded during TTS initialization
    print("🎌 Starting Nihongo Companion...")
    
    # Get actor count for confirmation
    print(f"✅ Voice options loaded with {tts.actor_count} actors")
    
    demo.title = "🎌 Nihongo Companion - AI Japanese Tutor"
    demo.description = "AI-powered Japanese language learning with natural voice synthesis"
    demo.launch(share=False)
