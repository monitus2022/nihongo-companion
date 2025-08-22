import yaml
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration manager for the avatar service."""

    def __init__(self, config_path: str = "./config/config.yaml"):
        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from a YAML file."""
        with open(self.config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        return self._config.get(key, default)

    @property
    def llm(self) -> Dict[str, Any]:
        return self._config.get("llm", {})

    @property
    def prompts(self) -> Dict[str, Any]:
        return self._config.get("prompts", {})

    @property
    def tts(self) -> Dict[str, Any]:
        return self._config.get("tts", {})

    @property
    def ui(self) -> Dict[str, Any]:
        return self._config.get("ui", {})

    @property
    def audio(self) -> Dict[str, Any]:
        return self._config.get("audio", {})

    @property
    def sliding_window(self) -> Dict[str, Any]:
        return self._config.get("sliding_window", {})

    @property
    def gui(self) -> Dict[str, Any]:
        return self._config.get("gui", {})

    @property
    def avatar(self) -> Dict[str, Any]:
        return self._config.get("avatar", {})

    @property
    def custom(self) -> Dict[str, Any]:
        return self._config.get("custom", {})

    @property
    def transport(self) -> Dict[str, Any]:
        return self._config.get("transport", {})

    @property
    def server(self) -> Dict[str, Any]:
        return self._config.get("server", {})

    @property
    def model_paths(self) -> Dict[str, Any]:
        return self._config.get("model_paths", {})

    @property
    def avatar_paths(self) -> Dict[str, Any]:
        return self._config.get("avatar_paths", {})

config = Config()
