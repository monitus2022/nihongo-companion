from ui import ChatInterface
from config import config
from utils import avatar_service_logger as logger

def main() -> None:
    logger.info("Starting Nihongo Companion - AI Japanese Tutor")
    
    # Create interface
    chat_interface = ChatInterface()
    app = chat_interface.create_interface()
    
    # Set app properties
    app.title = config.ui.get("title", "🎌 Nihongo Companion - AI Japanese Tutor")
    
    # Launch
    app.launch(share=config.ui.get("share", False))

if __name__ == "__main__":
    main()
    