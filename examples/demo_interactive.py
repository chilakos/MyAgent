"""Interactive chatbot demo with OpenAI.

Run with:
    python examples/demo_interactive.py
    
Type 'quit' to exit.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage, AIMessage
from src.core.llm import create_llm_provider
from src.core.config import settings


def main():
    """Run interactive chatbot."""
    print("=" * 60)
    print("Local Chatbot - OpenAI Interactive Demo")
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
        print(f"✓ Connected to {model_info['provider']}")
        print(f"  Model: {model_info['model']}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Conversation loop
    print("Type 'quit' to exit. Each response will cost a small amount.\n")
    conversation_history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            print("\nGoodbye!")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if not user_input:
            continue

        # Add user message to history
        conversation_history.append(HumanMessage(content=user_input))

        try:
            print("\nAssistant: ", end="", flush=True)
            response = llm.chat(conversation_history)
            print(response)
            print()

            # Add assistant response to history
            conversation_history.append(AIMessage(content=response))

        except Exception as e:
            print(f"Error: {e}\n")
            # Remove the message we tried to send if there was an error
            conversation_history.pop()


if __name__ == "__main__":
    main()
