"""Quick test of Gemini integration."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage
from src.core.llm import create_llm_provider
from src.core.config import settings


def main():
    """Test Gemini provider."""
    print("=" * 60)
    print("Testing Gemini LLM Integration")
    print("=" * 60)
    
    try:
        print(f"\nLLM Provider: {settings.llm_provider}")
        print(f"Gemini Model: {settings.gemini_model}")
        print(f"API Key: {settings.gemini_api_key[:20]}..." if settings.gemini_api_key else "No API key")
        
        # Create Gemini provider
        llm = create_llm_provider(
            provider_type="gemini",
            gemini_api_key=settings.gemini_api_key,
            gemini_model=settings.gemini_model,
        )
        
        print("\nInitializing Gemini...")
        llm.initialize()
        
        # Get model info
        model_info = llm.get_model_info()
        print(f"✓ Connected successfully!")
        print(f"  Provider: {model_info['provider']}")
        print(f"  Model: {model_info['model']}")
        print(f"  Type: {model_info['type']}")
        
        # Test a simple query
        print("\n" + "=" * 60)
        print("Testing Simple Query")
        print("=" * 60)
        
        messages = [HumanMessage(content="Hello! What is 2 + 2?")]
        print("\nQuery: 'Hello! What is 2 + 2?'")
        print("\nResponse:")
        response = llm.chat(messages)
        print(response)
        
        print("\n" + "=" * 60)
        print("✓ Gemini integration working!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
