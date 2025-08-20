from chat_interface import ChatInterface

app = ChatInterface()
ui = app.chat_interface

if __name__ == "__main__":
    print("🎌 Starting Nihongo Companion...")
    # Get actor count for confirmation
    print(f"✅ Voice options loaded with {len(app.actor_name_list)} actors")

    ui.title = "🎌 Nihongo Companion - AI Japanese Tutor"
    ui.description = "AI-powered Japanese language learning with natural voice synthesis"
    ui.launch(share=False)
