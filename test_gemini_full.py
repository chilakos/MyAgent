"""Test Gemini with proper waiting and timeout."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage
from src.core.llm import create_llm_provider
from src.core.config import settings
import time

print("=" * 70)
print("GEMINI TEST - Waiting for response (may take 30-60 seconds)")
print("=" * 70)

print(f"\nConfiguration:")
print(f"  Provider: {settings.llm_provider}")
print(f"  Model: {settings.gemini_model}")

# Create and initialize
llm = create_llm_provider(
    provider_type="gemini",
    gemini_api_key=settings.gemini_api_key,
    gemini_model=settings.gemini_model,
)

llm.initialize()
info = llm.get_model_info()
print(f"  Status: Connected")
print(f"  Model Info: {info}")

# Test with simple message
print("\n" + "=" * 70)
print("TEST 1: Simple greeting")
print("=" * 70)

messages = [HumanMessage(content="Say hello and tell me what you are")]

print("\nSending request...")
print("[Waiting for Gemini response...]")

start_time = time.time()
try:
    response = llm.chat(messages)
    elapsed = time.time() - start_time
    
    print(f"\nSuccess! Response received in {elapsed:.1f} seconds")
    print(f"\nResponse:\n{response}")
    
except KeyboardInterrupt:
    print("\n\n[INTERRUPTED by user]")
except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n[ERROR after {elapsed:.1f}s]: {type(e).__name__}")
    print(f"Message: {str(e)[:200]}")

# Test 2
print("\n" + "=" * 70)
print("TEST 2: Question")
print("=" * 70)

messages2 = [HumanMessage(content="What is 2 + 2?")]

print("\nSending request...")
print("[Waiting for Gemini response...]")

start_time = time.time()
try:
    response2 = llm.chat(messages2)
    elapsed = time.time() - start_time
    
    print(f"\nSuccess! Response received in {elapsed:.1f} seconds")
    print(f"\nResponse:\n{response2}")
    
except KeyboardInterrupt:
    print("\n\n[INTERRUPTED by user]")
except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n[ERROR after {elapsed:.1f}s]: {type(e).__name__}")
    print(f"Message: {str(e)[:200]}")

print("\n" + "=" * 70)
print("Test complete")
print("=" * 70)
