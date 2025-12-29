"""Simple demo script to interact with the LLM abstraction layer.

Run with:
    python examples/demo.py
"""

from langchain_core.messages import HumanMessage, AIMessage
from src.core.llm import create_llm_provider
from src.core.config import settings


def main():
    """Run interactive demo."""
    print("=" * 60)
    print("Local Chatbot - LLM Abstraction Demo")
    print("=" * 60)
    print(f"\nUsing provider: {settings.llm_provider}")
    print(f"Model: {settings.ollama_model if settings.llm_provider == 'ollama' else settings.openai_model}")
    print()

    # Create provider
    try:
        if settings.llm_provider == "ollama":
            llm = create_llm_provider(
                provider_type="ollama",
                ollama_base_url=settings.ollama_base_url,
                ollama_model=settings.ollama_model,
            )
            print(f"Connecting to Ollama at {settings.ollama_base_url}...")
        else:
            if not settings.openai_api_key:
                print("ERROR: OpenAI API key not set in .env")
                print("Set OPENAI_API_KEY in .env file to use OpenAI provider")
                return
            llm = create_llm_provider(
                provider_type="openai",
                openai_api_key=settings.openai_api_key,
                openai_model=settings.openai_model,
            )
            print("Using OpenAI provider...")

        llm.initialize()
        model_info = llm.get_model_info()
        print(f"✓ Connected successfully!")
        print(f"  Provider: {model_info['provider']}")
        print(f"  Model: {model_info['model']}")
        print()
    except Exception as e:
        print(f"✗ Error initializing LLM: {e}")
        print("\nTroubleshooting:")
        if settings.llm_provider == "ollama":
            print("  1. Is Ollama running? Start it with: ollama serve")
            print("  2. Do you have the model? Download it with: ollama pull mistral")
        else:
            print("  1. Is OPENAI_API_KEY set in .env?")
        return

    # Conversation loop
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
