from core.tts import TextToSpeechHandler
from core.llm import prompt_llm
from config import config
import gradio as gr

class ChatInterface:
    def __init__(self):
        self.tts = TextToSpeechHandler()
        # Cache voice style info
        self.actor_name_list = self.tts.voice_style_info.get("actors", [])
        self.actor_style_dict = self.tts.voice_style_info.get("actor_styles", {})
        self.style_lookup_dict = self.tts.voice_style_info.get("style_lookup", {})
        self.chat_interface = self.create_interface()

    def create_output_to_ui(
        self,
        llm_model_name: str,
        voice_actor_name: str,
        voice_style_name: str,
        admin_prompt: str | None,
        user_prompt: str,
    ) -> tuple[str, str]:
        """
        Gradio UI parameters, pass user input into related functions
        """
        print(f"Creating media output with actor: {voice_actor_name}, style: {voice_style_name}")
        if not admin_prompt:
            admin_prompt = config.prompts.get("default_admin", "")
        llm_response = prompt_llm(
            user_prompt=user_prompt,
            admin_prompt=admin_prompt,
            llm_model_name=llm_model_name,
        )
        if llm_response:
            self.tts.create_wav_from_llm_response(
                llm_response=llm_response,
                voice_actor_name=voice_actor_name,
                voice_style_name=voice_style_name,
            )
        return llm_response, self.tts.wav_output_path

    def fetch_available_style_names_given_actor_name(self, actor_name: str) -> list[str]:
        return self.actor_style_dict.get(actor_name, [])

    def create_interface(self):
        """
        Create the Gradio interface for the chat application.
        """
        with gr.Blocks(
            title=config.ui.get("title", ""),
            theme=gr.themes.Ocean(),    # https://www.gradio.app/guides/theming-guide
            ) as app:
            gr.Markdown(config.ui.get("header", ""))
            
            # Usage instructions paragraph
            gr.Markdown(config.ui.get("instruction", ""))

            with gr.Row():
                # Left column: user input
                with gr.Column():
                    llm_model_name = gr.Textbox(label="LLM Model Name", value="gemma3", placeholder="Enter model name")

                    # Dynamic voice selection with safe initialization
                    initial_actor = self.actor_name_list[0]
                    initial_styles = self.fetch_available_style_names_given_actor_name(initial_actor)
                    initial_style = initial_styles[0]
                    
                    voice_actor = gr.Dropdown(
                        label="Voice Actor", 
                        choices=self.actor_name_list, 
                        value=initial_actor
                    )
                    voice_style = gr.Dropdown(
                        label="Voice Style", 
                        choices=initial_styles,
                        value=initial_style
                    )
                    admin_prompt = gr.Textbox(
                        label="Admin Prompt (Optional)", 
                        placeholder="Optional admin guidance, will replace default prompt"
                        )
                    user_prompt = gr.Textbox(
                        label="User Prompt", 
                        value=config.prompts.get("default_user", ""), 
                        placeholder="Enter your prompt here"
                        )
                    submit_btn = gr.Button(
                        "Generate Response & Audio", 
                        variant="primary"
                        )
                
                # Right column: text and media output
                with gr.Column():
                    text_output = gr.Textbox(
                        label="Model Response"
                        )
                    audio_output = gr.Audio(
                        label="Generated Speech", 
                        type="filepath",
                        autoplay=True
                    )

            # Update voice style choices when voice actor changes
            def update_voice_styles(voice_actor_name):
                styles = self.fetch_available_style_names_given_actor_name(voice_actor_name)
                return gr.Dropdown(choices=styles, value=styles[0] if styles else "N/A")

            voice_actor.change(
                fn=update_voice_styles,
                inputs=[voice_actor],
                outputs=[voice_style]
            )
            
            # Handle from pressing "enter" in User Prompt Box
            user_prompt.submit(
                fn=self.create_output_to_ui,
                inputs=[llm_model_name, voice_actor, voice_style, admin_prompt, user_prompt],
                outputs=[text_output, audio_output]
            )

            # Handle from submission button click
            submit_btn.click(
                fn=self.create_output_to_ui,
                inputs=[llm_model_name, voice_actor, voice_style, admin_prompt, user_prompt],
                outputs=[text_output, audio_output]
            )
    
        return app
    