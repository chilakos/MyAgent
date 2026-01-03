"""Demo script with mocked LLM responses - no API required!

Run with:
    python examples/demo_mock.py
"""

from unittest.mock import MagicMock
from langchain_core.messages import HumanMessage, AIMessage
from src.core.llm import OllamaProvider, OpenAIProvider


def main():
    """Run demo with mocked responses."""
    print("=" * 60)
    print("Local Chatbot - Mock Demo (No API Required!)")
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

    # Sample mock responses
    mock_responses = [
        "Hello! I'm a mock chatbot. How can I help you?",
        "That's an interesting question! In the mock world, everything is possible.",
        "I understand. Let me think about that... Done! The answer is 42.",
        "Great question! I don't have a real answer, but I'm demonstrating the chatbot flow.",
    ]

    response_idx = 0

    # Configuration
    print(f"Provider: Mocked Ollama")
    print(f"Model: mistral")
    print(f"Status: ✓ Connected (mock mode)\n")
    print("Type 'quit' to exit\n")

    conversation_history = []

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if not user_input:
            continue

        # Add user message to history
        conversation_history.append(HumanMessage(content=user_input))

        # Mock the chat response
        mock_response = mock_responses[response_idx % len(mock_responses)]
        mock_client.invoke.return_value = MagicMock(content=mock_response)

        response = mock_client.invoke(conversation_history).content

        print(f"\nAssistant: {response}\n")

        # Add assistant response to history
        conversation_history.append(AIMessage(content=response))

        response_idx += 1

        # Show conversation history
        print("--- Conversation History ---")
        for i, msg in enumerate(conversation_history, 1):
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            print(f"{i}. {role}: {msg.content[:50]}...")
        print()


if __name__ == "__main__":
    main()
