"""Quick Ollama test."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage
from src.core.llm import create_llm_provider
from src.core.config import settings
import time

print("=" * 70)
print("OLLAMA LOCAL TEST")
print("=" * 70)

print(f"\nConfiguration:")
print(f"  Provider: {settings.llm_provider}")
print(f"  Base URL: {settings.ollama_base_url}")
print(f"  Model: {settings.ollama_model}")

try:
    # Create and initialize
    llm = create_llm_provider(
        provider_type="ollama",
        ollama_base_url=settings.ollama_base_url,
        ollama_model=settings.ollama_model,
    )
    
    print("\nConnecting to Ollama...")
    llm.initialize()
    info = llm.get_model_info()
    print(f"✓ Connected!")
    print(f"  Provider: {info['provider']}")
    print(f"  Model: {info['model']}")
    print(f"  Type: {info['type']}")
    
    # Test message
    print("\n" + "=" * 70)
    print("TEST: Simple greeting")
    print("=" * 70)
    
    messages = [HumanMessage(content="Hello! What are you?")]
    
    print("\nSending: 'Hello! What are you?'")
    start = time.time()
    response = llm.chat(messages)
    elapsed = time.time() - start
    
    print(f"\nResponse received in {elapsed:.1f}s:")
    print(f"{response}")
    
except ConnectionError as e:
    print(f"\n✗ Cannot connect to Ollama")
    print(f"  Make sure Ollama is running: ollama serve")
    print(f"  Error: {e}")
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}")
    print(f"  {e}")
