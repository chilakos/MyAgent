"""Quick test to see if OpenAI connection works."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.llm import create_llm_provider
from src.core.config import settings

print("=" * 60)
print("OpenAI Integration Test")
print("=" * 60)
print()
print(f"LLM Provider: {settings.llm_provider}")
print(f"Model: {settings.openai_model}")
print(f"API Key present: {'Yes' if settings.openai_api_key else 'No'}")
print()

try:
    print("Creating provider...")
    llm = create_llm_provider(
        provider_type=settings.llm_provider,
        openai_api_key=settings.openai_api_key,
        openai_model=settings.openai_model,
    )
    
    print("Initializing client...")
    llm.initialize()
    
    print("✓ OpenAI connected successfully!")
    print()
    print("Model info:")
    info = llm.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
