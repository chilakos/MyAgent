"""Automated test of the interactive demo with real OpenAI."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage, AIMessage
from src.core.llm import create_llm_provider
from src.core.config import settings


def demo():
    """Simulate a conversation with OpenAI."""
    print("=" * 60)
    print("Local Chatbot - OpenAI Live Demo")
    print("=" * 60)
    print()

    # Create provider
    try:
        llm = create_llm_provider(
            provider_type="openai",
            openai_api_key=settings.openai_api_key,
            openai_model=settings.openai_model,
        )
        
        llm.initialize()
        model_info = llm.get_model_info()
        print(f"✓ Connected to OpenAI")
        print(f"  Model: {model_info['model']}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return

    # Simulate a conversation
    test_messages = [
        "Hello! What is Python and why is it popular?",
        "Can you give me a short example of Python code?",
        "How does Git help with version control?",
    ]

    conversation_history = []

    for user_msg in test_messages:
        # Add user message
        conversation_history.append(HumanMessage(content=user_msg))
        print(f"You: {user_msg}")

        try:
            # Get response from OpenAI
            response = llm.chat(conversation_history)
            
            # Print response
            print(f"Assistant: {response}")
            print()

            # Add assistant response to history
            conversation_history.append(AIMessage(content=response))

        except Exception as e:
            print(f"Error: {e}\n")
            conversation_history.pop()

    # Show final history
    print("=" * 60)
    print("Conversation Summary")
    print("=" * 60)
    for i, msg in enumerate(conversation_history, 1):
        role = "👤 You" if isinstance(msg, HumanMessage) else "🤖 Assistant"
        content = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
        print(f"{i}. {role}: {content}")

    print()
    print(f"Total messages: {len(conversation_history)}")
    print("✓ Demo complete!")


if __name__ == "__main__":
    demo()
