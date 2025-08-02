import yaml
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field, field_validator

"""
Configuration loader for the Ollama service.
Loads settings from config.yaml file with Pydantic validation.
"""


class PromptsConfig(BaseModel):
    """Configuration for default prompts."""
    default_admin: str = Field(..., description="Default admin prompt for the model")
    default_user: str = Field(..., description="Default user prompt")


class ModelsConfig(BaseModel):
    """Configuration for model settings."""
    default: str = Field(..., description="Default model name")
    available: List[str] = Field(..., description="List of available models")
    
    @field_validator('default')
    @classmethod
    def default_must_be_in_available(cls, v, info):
        if 'available' in info.data and v not in info.data['available']:
            raise ValueError(f"Default model '{v}' must be in available models list")
        return v


class APIConfig(BaseModel):
    """Configuration for API settings."""
    title: str = Field(..., description="API title")
    description: str = Field(..., description="API description")
    version: str = Field(..., description="API version")


class ServiceConfig(BaseModel):
    """Configuration for service settings."""
    name: str = Field(..., description="Service name")
    host: str = Field("0.0.0.0", description="Service host")
    port: int = Field(8000, description="Service port")
    
    @field_validator('port')
    @classmethod
    def port_must_be_valid(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v


class OllamaConfig(BaseModel):
    """Configuration for Ollama connection."""
    host: str = Field("localhost", description="Ollama host")
    port: int = Field(11434, description="Ollama port")
    timeout: int = Field(30, description="Timeout in seconds")
    
    @field_validator('port')
    @classmethod
    def port_must_be_valid(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v
    
    @field_validator('timeout')
    @classmethod
    def timeout_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v
    
    @property
    def base_url(self) -> str:
        """Get the full Ollama base URL."""
        return f"http://{self.host}:{self.port}"


class ResponseConfig(BaseModel):
    """Configuration for response settings."""
    max_length: int = Field(1000, description="Maximum response length")
    timeout: int = Field(30, description="Response timeout in seconds")
    
    @field_validator('max_length')
    @classmethod
    def max_length_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Max length must be positive")
        return v
    
    @field_validator('timeout')
    @classmethod
    def timeout_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v


class LoggingConfig(BaseModel):
    """Configuration for logging settings."""
    level: str = Field("INFO", description="Logging level")
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Logging format"
    )
    
    @field_validator('level')
    @classmethod
    def level_must_be_valid(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Logging level must be one of {valid_levels}")
        return v.upper()


class AppConfig(BaseModel):
    """Main application configuration."""
    prompts: PromptsConfig
    models: ModelsConfig
    api: APIConfig
    service: ServiceConfig
    ollama: OllamaConfig
    response: ResponseConfig
    logging: LoggingConfig

# Get the directory where this config.py file is located and go up one level
CONFIG_DIR = Path(__file__).parent.parent
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def load_config() -> AppConfig:
    """
    Load configuration from YAML file and validate with Pydantic.
    
    Returns:
        AppConfig: Validated configuration object
        
    Raises:
        FileNotFoundError: If config.yaml is not found
        yaml.YAMLError: If YAML parsing fails
        ValidationError: If configuration validation fails
    """
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
            config_dict = yaml.safe_load(file)
        
        # Create and validate configuration using Pydantic
        config = AppConfig(**config_dict)
        return config
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_FILE}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML configuration: {e}")


# Load and validate configuration
config = load_config()

# Export commonly used values for backward compatibility
DEFAULT_ADMIN_PROMPT = config.prompts.default_admin
DEFAULT_USER_PROMPT = config.prompts.default_user

DEFAULT_MODEL = config.models.default
AVAILABLE_MODELS = config.models.available

API_TITLE = config.api.title
API_DESCRIPTION = config.api.description
API_VERSION = config.api.version

SERVICE_NAME = config.service.name
SERVICE_HOST = config.service.host
SERVICE_PORT = config.service.port

OLLAMA_HOST = config.ollama.host
OLLAMA_PORT = config.ollama.port
OLLAMA_BASE_URL = config.ollama.base_url
OLLAMA_TIMEOUT = config.ollama.timeout

MAX_RESPONSE_LENGTH = config.response.max_length
DEFAULT_TIMEOUT = config.response.timeout

LOGGING_LEVEL = config.logging.level
LOGGING_FORMAT = config.logging.format


def get_config() -> AppConfig:
    """
    Get the full configuration object.
    
    Returns:
        AppConfig: Complete validated configuration
    """
    return config


def get_config_value(key_path: str, default=None):
    """
    Get a nested configuration value using dot notation.
    
    Args:
        key_path (str): Dot-separated path to the config value (e.g., 'service.port')
        default: Default value if key is not found
        
    Returns:
        Any: Configuration value or default
        
    Example:
        get_config_value('service.port')  # Returns 8000
        get_config_value('models.default')  # Returns 'jp-gemma3'
    """
    try:
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            value = getattr(value, key)
        return value
    except (AttributeError, TypeError):
        return default
