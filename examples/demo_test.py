"""Demo test of personal agent with Gemini."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage, AIMessage
from src.core.llm import create_llm_provider
from src.core.config import settings
from src.core.memory import ConversationManager, ConversationType


def main():
    """Run a quick demo of the personal agent."""
    print("=" * 60)
    print("Personal Agent with Gemini & Memory")
    print("=" * 60)
    
    # Initialize
    memory_manager = ConversationManager()
    
    llm = create_llm_provider(
        provider_type="gemini",
        gemini_api_key=settings.gemini_api_key,
        gemini_model=settings.gemini_model,
    )
    
    llm.initialize()
    model_info = llm.get_model_info()
    print(f"\n✓ Connected to {model_info['provider']} - {model_info['model']}")
    print(f"✓ Memory ready (data/conversations.db)")
    
    # Create new daily check-in conversation
    print("\n" + "=" * 60)
    print("Starting Daily Check-in")
    print("=" * 60)
    
    conv_id = memory_manager.create_conversation(
        conv_type=ConversationType.DAILY_CHECKIN,
        title="Daily Check-in - 2025-01-02"
    )
    print(f"\n✓ Created conversation: {conv_id[:8]}...")
    
    # Have a conversation
    conversation_history = []
    questions = [
        "What are my top 3 priorities for today?",
        "Help me break down how to achieve them.",
    ]
    
    for question in questions:
        print(f"\n[You]: {question}")
        conversation_history.append(HumanMessage(content=question))
        
        print("[Gemini]: ", end="", flush=True)
        try:
            response = llm.chat(conversation_history)
            print(response)
            conversation_history.append(AIMessage(content=response))
        except Exception as e:
            print(f"\n✗ Error: {e}")
            break
    
    # Save conversation
    if conversation_history:
        memory_manager.save_conversation(conv_id, conversation_history)
        print(f"\n✓ Saved conversation ({len(conversation_history)} messages)")
    
    # List conversations
    print("\n" + "=" * 60)
    print("Recent Conversations")
    print("=" * 60)
    
    conversations = memory_manager.list_conversations(limit=5)
    for conv in conversations:
        print(f"  {conv['id'][:8]}... | {conv['type']:15} | {conv['created_at'][:10]}")
    
    print("\n" + "=" * 60)
    print("✓ Demo complete!")
    print("Run 'python examples/demo.py' for interactive mode")
    print("=" * 60)


if __name__ == "__main__":
    main()
