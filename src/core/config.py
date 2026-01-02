"""Configuration module for LLM and API settings."""

import os
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # LLM Configuration
    llm_provider: Literal["ollama", "openai", "gemini"] = os.getenv("LLM_PROVIDER", "ollama")
    
    # Ollama settings
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "mistral")
    
    # OpenAI settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Gemini settings
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Testing
    use_real_api: bool = os.getenv("USE_REAL_API", "false").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
