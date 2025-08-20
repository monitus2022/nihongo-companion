# from chat_interface import ChatInterface
# from config import config
# import gradio as gr

# app = ChatInterface()
# ui = app.chat_interface

# if __name__ == "__main__":
#     print("🎌 Starting Nihongo Companion...")
#     # Get actor count for confirmation
#     print(f"✅ Voice options loaded with {len(app.actor_name_list)} actors")

#     ui.title = config.ui.get("title")
#     ui.description = config.ui.get("description")
#     ui.launch(
#         share=config.ui.get("share", False)
#         )

from ui import ChatInterface
from config import config

def main():
    print("🎌 Starting Nihongo Companion Avatar Service...")
    
    # Create interface using existing code
    chat_interface = ChatInterface()
    app = chat_interface.create_interface()
    
    # Set demo properties
    app.title = config.ui.get("title", "🎌 Nihongo Companion - AI Japanese Tutor")
    
    # Launch
    app.launch(share=config.ui.get("share", False))

if __name__ == "__main__":
    main()