"""Shared pytest fixtures and configuration."""

import os
from unittest.mock import MagicMock

import pytest


# Configuration
USE_REAL_API = os.getenv("USE_REAL_API", "false").lower() == "true"


@pytest.fixture
def mock_llm_response():
    """Fixture for mock LLM response."""
    return MagicMock(content="This is a test response from the LLM")


@pytest.fixture
def mock_llm_chat(mocker):
    """Fixture for mocked ChatOllama/ChatOpenAI."""
    mock = mocker.patch("langchain_ollama.ChatOllama")
    mock.return_value.invoke.return_value = MagicMock(
        content="Mocked LLM response"
    )
    return mock


@pytest.fixture
def mock_conversation_history():
    """Fixture for mock conversation history."""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there! How can I help?"},
    ]


@pytest.fixture
def test_env(monkeypatch):
    """Fixture to set test environment variables."""
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "mistral")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("USE_REAL_API", "false")
