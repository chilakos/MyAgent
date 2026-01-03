"""LLM abstraction layer for swappable provider support."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.messages import BaseMessage


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the LLM provider."""
        pass

    @abstractmethod
    def chat(self, messages: list[BaseMessage], **kwargs: Any) -> str:
        """Send messages to LLM and get response.

        Args:
            messages: List of messages in conversation.
            **kwargs: Additional parameters (temperature, max_tokens, etc).

        Returns:
            Response text from the LLM.
        """
        pass

    @abstractmethod
    def get_model_info(self) -> dict[str, Any]:
        """Get information about the current model.

        Returns:
            Dictionary with model info (name, version, capabilities, etc).
        """
        pass


class OllamaProvider(LLMProvider):
    """Ollama LLM provider for local models."""

    def __init__(self, base_url: str, model: str):
        """Initialize Ollama provider.

        Args:
            base_url: Base URL for Ollama (e.g., http://localhost:11434)
            model: Model name (e.g., mistral, llama2)
        """
        self.base_url = base_url
        self.model = model
        self.client = None

    def initialize(self) -> None:
        """Initialize Ollama client."""
        try:
            from langchain_ollama import ChatOllama

            self.client = ChatOllama(model=self.model, base_url=self.base_url)
        except ImportError as e:
            raise ImportError("langchain-ollama not installed. Install with: pip install langchain-ollama")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Ollama: {e}")

    def chat(self, messages: list[BaseMessage], **kwargs: Any) -> str:
        """Get response from Ollama.

        Args:
            messages: List of messages.
            **kwargs: Additional parameters.

        Returns:
            Response text from Ollama.
        """
        if not self.client:
            self.initialize()

        response = self.client.invoke(messages, **kwargs)
        return response.content

    def get_model_info(self) -> dict[str, Any]:
        """Get Ollama model information."""
        return {
            "provider": "ollama",
            "model": self.model,
            "base_url": self.base_url,
            "type": "local",
        }


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider for cloud-based models."""

    def __init__(self, api_key: str, model: str):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key.
            model: Model name (e.g., gpt-4o-mini, gpt-3.5-turbo).
        """
        self.api_key = api_key
        self.model = model
        self.client = None

    def initialize(self) -> None:
        """Initialize OpenAI client."""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        try:
            from langchain_openai import ChatOpenAI

            self.client = ChatOpenAI(model=self.model, api_key=self.api_key)
        except ImportError as e:
            raise ImportError("langchain-openai not installed. Install with: pip install langchain-openai")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI: {e}")

    def chat(self, messages: list[BaseMessage], **kwargs: Any) -> str:
        """Get response from OpenAI.

        Args:
            messages: List of messages.
            **kwargs: Additional parameters.

        Returns:
            Response text from OpenAI.
        """
        if not self.client:
            self.initialize()

        response = self.client.invoke(messages, **kwargs)
        return response.content

    def get_model_info(self) -> dict[str, Any]:
        """Get OpenAI model information."""
        return {
            "provider": "openai",
            "model": self.model,
            "type": "cloud",
        }


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider for cloud-based models."""

    def __init__(self, api_key: str, model: str):
        """Initialize Gemini provider.

        Args:
            api_key: Google Gemini API key.
            model: Model name (e.g., gemini-1.5-flash, gemini-1.5-pro).
        """
        self.api_key = api_key
        self.model = model
        self.client = None

    def initialize(self) -> None:
        """Initialize Gemini client."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            self.client = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self.api_key,
                temperature=0.7,
            )
        except ImportError as e:
            raise ImportError("langchain-google-genai not installed. Install with: pip install langchain-google-genai")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini: {e}")

    def chat(self, messages: list[BaseMessage], **kwargs: Any) -> str:
        """Get response from Gemini.

        Args:
            messages: List of messages.
            **kwargs: Additional parameters.

        Returns:
            Response text from Gemini.
        """
        if not self.client:
            self.initialize()

        response = self.client.invoke(messages, **kwargs)
        return response.content

    def get_model_info(self) -> dict[str, Any]:
        """Get Gemini model information."""
        return {
            "provider": "gemini",
            "model": self.model,
            "type": "cloud",
        }


def create_llm_provider(
    provider_type: str = "ollama",
    ollama_base_url: Optional[str] = None,
    ollama_model: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    openai_model: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    gemini_model: Optional[str] = None,
) -> LLMProvider:
    """Factory function to create LLM provider.

    Args:
        provider_type: Type of provider ('ollama', 'openai', or 'gemini').
        ollama_base_url: Ollama base URL (used if provider_type='ollama').
        ollama_model: Ollama model name (used if provider_type='ollama').
        openai_api_key: OpenAI API key (used if provider_type='openai').
        openai_model: OpenAI model name (used if provider_type='openai').
        gemini_api_key: Google Gemini API key (used if provider_type='gemini').
        gemini_model: Google Gemini model name (used if provider_type='gemini').

    Returns:
        Initialized LLM provider instance.

    Raises:
        ValueError: If provider_type is unknown or required params missing.
    """
    if provider_type.lower() == "ollama":
        if not ollama_base_url or not ollama_model:
            raise ValueError("ollama_base_url and ollama_model required for Ollama provider")
        provider = OllamaProvider(base_url=ollama_base_url, model=ollama_model)
    elif provider_type.lower() == "openai":
        if not openai_api_key or not openai_model:
            raise ValueError("openai_api_key and openai_model required for OpenAI provider")
        provider = OpenAIProvider(api_key=openai_api_key, model=openai_model)
    elif provider_type.lower() == "gemini":
        if not gemini_api_key or not gemini_model:
            raise ValueError("gemini_api_key and gemini_model required for Gemini provider")
        provider = GeminiProvider(api_key=gemini_api_key, model=gemini_model)
    else:
        raise ValueError(f"Unknown LLM provider: {provider_type}")

    return provider
