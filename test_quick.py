"""Quick connection test for Gemini."""

from src.core.llm import create_llm_provider

try:
    print("Creating Gemini provider...")
    llm = create_llm_provider(
        provider_type='gemini',
        gemini_api_key='AIzaSyD9xX_XPRSJWoY1WSguIYxEPuR6KO3qm_4',
        gemini_model='gemini-2.0-flash'
    )
    
    print("Initializing...")
    llm.initialize()
    
    print("Getting model info...")
    info = llm.get_model_info()
    print(f"✓ Connected: {info}")
    
except Exception as e:
    print(f"✗ Error: {e}")
