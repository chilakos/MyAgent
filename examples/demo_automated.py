"""Automated test of the mock demo to show interaction."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock
from langchain_core.messages import HumanMessage, AIMessage

# Now import our modules
import importlib
llm_module = importlib.import_module('src.core.llm')
OllamaProvider = llm_module.OllamaProvider


def demo():
    """Simulate a conversation without user input."""
    print("=" * 60)
    print("Local Chatbot - Interactive Demo (Simulated)")
    print("=" * 60)
    print()

    # Create a mock LLM provider
    provider = OllamaProvider(
        base_url="http://localhost:11434",
        model="mistral",
    )

    # Create mock client
    mock_client = MagicMock()
    provider.client = mock_client

    print(f"Provider: Mocked Ollama")
    print(f"Model: mistral")
    print(f"Status: ✓ Connected (mock mode)\n")
    print("-" * 60)

    conversation_history = []

    # Simulate a conversation
    test_exchanges = [
        ("Hello, how are you?", "I'm doing great, thank you for asking! How can I assist you today?"),
        ("What is Python?", "Python is a powerful, versatile programming language known for its simplicity and readability. It's widely used in web development, data science, automation, and more."),
        ("Can you help me learn Git?", "Absolutely! Git is a version control system that helps you track changes in your code. Would you like to learn about branching, commits, or PRs?"),
    ]

    for user_msg, bot_response in test_exchanges:
        # Add user message
        conversation_history.append(HumanMessage(content=user_msg))
        print(f"\nYou: {user_msg}")

        # Mock the response
        mock_client.invoke.return_value = MagicMock(content=bot_response)
        response = mock_client.invoke(conversation_history).content

        print(f"Assistant: {response}")

        # Add assistant response to history
        conversation_history.append(AIMessage(content=response))

    # Show final conversation history
    print("\n" + "=" * 60)
    print("Conversation History")
    print("=" * 60)
    for i, msg in enumerate(conversation_history, 1):
        role = "👤 You" if isinstance(msg, HumanMessage) else "🤖 Assistant"
        print(f"\n{i}. {role}:")
        print(f"   {msg.content}")

    print("\n" + "=" * 60)
    print(f"Total messages in history: {len(conversation_history)}")
    print("✓ Demo complete!")


if __name__ == "__main__":
    demo()
