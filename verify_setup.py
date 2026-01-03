"""Verification that Gemini integration is ready."""

from langchain_core.messages import HumanMessage
from src.core.llm import create_llm_provider
from src.core.memory import ConversationManager

print("\n" + "="*60)
print("Gemini Integration Verification")
print("="*60)

# Test memory
memory = ConversationManager()
print(f"✓ Memory system ready (data/conversations.db)")

# Test Gemini connection
llm = create_llm_provider(
    provider_type='gemini',
    gemini_api_key='AIzaSyD9xX_XPRSJWoY1WSguIYxEPuR6KO3qm_4',
    gemini_model='gemini-2.0-flash'
)

llm.initialize()
info = llm.get_model_info()
print(f"✓ Gemini LLM ready")
print(f"  Provider: {info['provider']}")
print(f"  Model: {info['model']}")

print("\n" + "="*60)
print("Ready to start! Run:")
print("  python examples/demo.py")
print("="*60 + "\n")
