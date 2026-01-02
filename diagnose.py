"""Diagnose Gemini API issues."""

import os
from src.core.config import settings

print("Gemini Configuration:")
print(f"  Provider: {settings.llm_provider}")
print(f"  Model: {settings.gemini_model}")
print(f"  API Key Present: {bool(settings.gemini_api_key)}")
print(f"  API Key Length: {len(settings.gemini_api_key) if settings.gemini_api_key else 0}")

if settings.gemini_api_key:
    print(f"  API Key (first 20 chars): {settings.gemini_api_key[:20]}...")
    
    # Try to import and test the library
    print("\nTesting Gemini library imports...")
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("  [OK] langchain_google_genai imported successfully")
        
        # Try to create client
        print("\nCreating Gemini client...")
        client = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=0.7,
        )
        print("  [OK] Client created successfully")
        
        # Try to call it with a timeout
        print("\nAttempting simple API call (this may take 10-30 seconds)...")
        from langchain_core.messages import HumanMessage
        
        result = client.invoke([HumanMessage(content="Hi")], timeout=60)
        print("  [OK] API call succeeded!")
        print(f"  Response (first 100 chars): {result.content[:100]}")
        
    except ImportError as e:
        print(f"  [ERROR] Import error: {e}")
    except TimeoutError as e:
        print(f"  [TIMEOUT] API call timed out after 60s: {e}")
    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}: {str(e)[:200]}")
else:
    print("[ERROR] No Gemini API key found!")
