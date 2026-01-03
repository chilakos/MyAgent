"""Test Gemini response time."""

import time
from langchain_core.messages import HumanMessage
from src.core.llm import create_llm_provider
from src.core.config import settings

print("Testing Gemini response speed...\n")

llm = create_llm_provider(
    provider_type="gemini",
    gemini_api_key=settings.gemini_api_key,
    gemini_model=settings.gemini_model,
)

llm.initialize()

# Simple test
messages = [HumanMessage(content="Say 'hello world' and nothing else.")]

print("Sending request to Gemini...")
start = time.time()

try:
    response = llm.chat(messages)
    elapsed = time.time() - start
    
    print(f"✓ Got response in {elapsed:.1f}s")
    print(f"Response: {response}")
    
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ Error after {elapsed:.1f}s: {e}")
