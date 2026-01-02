"""Simple demo script to interact with the LLM abstraction layer.

Run with:
    python examples/demo.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage, AIMessage
from src.core.llm import create_llm_provider
from src.core.config import settings
from src.core.memory import ConversationManager, ConversationType


def main():
    """Run interactive demo."""
    print("=" * 60)
    print("Local Chatbot - Personal Agent")
    print("=" * 60)
    print(f"\nUsing provider: {settings.llm_provider}")
    print(f"Model: {settings.ollama_model if settings.llm_provider == 'ollama' else settings.openai_model}")
    print()

    # Initialize conversation manager
    memory_manager = ConversationManager()

    # Create provider
    try:
        if settings.llm_provider == "ollama":
            llm = create_llm_provider(
                provider_type="ollama",
                ollama_base_url=settings.ollama_base_url,
                ollama_model=settings.ollama_model,
            )
            print(f"Connecting to Ollama at {settings.ollama_base_url}...")
        elif settings.llm_provider == "openai":
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
        elif settings.llm_provider == "gemini":
            if not settings.gemini_api_key:
                print("ERROR: Gemini API key not set in .env")
                print("Set GEMINI_API_KEY in .env file to use Gemini provider")
                return
            llm = create_llm_provider(
                provider_type="gemini",
                gemini_api_key=settings.gemini_api_key,
                gemini_model=settings.gemini_model,
            )
            print("Using Google Gemini provider...")
        else:
            print(f"ERROR: Unknown LLM provider: {settings.llm_provider}")
            return

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

    # Check for existing conversation or start new one
    print("\n[Options]")
    print("  'new <type>' - Start new conversation (daily_checkin, weekly_review, routine, finance, goals, general)")
    print("  'list' - Show recent conversations")
    print("  'quit' - Exit\n")

    conversation_id = None
    conversation_history = []

    # Try to load previous session
    latest = memory_manager.get_latest_conversation()
    if latest:
        print(f"✓ Loaded previous conversation: {latest['type']} from {latest['created_at'][:10]}")
        conversation_id = latest["id"]
        conversation_history = latest["messages"]
        print(f"  {len(conversation_history)} messages in history\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("quit", "exit", "q"):
            if conversation_id and conversation_history:
                memory_manager.save_conversation(conversation_id, conversation_history)
                print(f"✓ Conversation saved ({len(conversation_history)} messages)")
            print("Goodbye!")
            break

        if user_input.lower() == "list":
            conversations = memory_manager.list_conversations(limit=5)
            if conversations:
                print("\n[Recent Conversations]")
                for conv in conversations:
                    print(f"  {conv['id'][:8]}... | {conv['type']:15} | {conv['created_at'][:10]}")
                print()
            else:
                print("No conversations yet.\n")
            continue

        if user_input.lower().startswith("new "):
            # Save previous conversation if exists
            if conversation_id and conversation_history:
                memory_manager.save_conversation(conversation_id, conversation_history)
                print(f"✓ Saved previous conversation\n")

            # Start new conversation
            conv_type = user_input[4:].strip()
            try:
                conversation_id = memory_manager.create_conversation(
                    conv_type=conv_type,
                    title=f"{conv_type} - {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                conversation_history = []
                print(f"✓ Started new {conv_type} conversation\n")
            except ValueError:
                print(f"Invalid conversation type. Use: daily_checkin, weekly_review, routine, finance, goals, general\n")
            continue

        if not user_input:
            continue

        # Create conversation if none exists
        if not conversation_id:
            conversation_id = memory_manager.create_conversation(
                conv_type=ConversationType.GENERAL,
                title=f"General - {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )

        # Add user message to history
        conversation_history.append(HumanMessage(content=user_input))

        try:
            print("\nAssistant: ", end="", flush=True)
            print("[Thinking...]", flush=True)
            response = llm.chat(conversation_history)
            # Clear the waiting message and print response
            print("\r" + " " * 30 + "\r", end="", flush=True)
            print(response)
            print()

            # Add assistant response to history
            conversation_history.append(AIMessage(content=response))

            # Auto-save after each exchange
            memory_manager.save_conversation(conversation_id, conversation_history)

        except Exception as e:
            print(f"Error: {e}\n")
            # Remove the message we tried to send if there was an error
            conversation_history.pop()


if __name__ == "__main__":
    main()
