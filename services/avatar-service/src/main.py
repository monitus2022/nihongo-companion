from chat_interface import ChatInterface
from config import config
import gradio as gr

app = ChatInterface()
ui = app.chat_interface

if __name__ == "__main__":
    print("🎌 Starting Nihongo Companion...")
    # Get actor count for confirmation
    print(f"✅ Voice options loaded with {len(app.actor_name_list)} actors")

    ui.title = config.ui.get("title")
    ui.description = config.ui.get("description")
    ui.launch(
        share=config.ui.get("share", False)
        )
