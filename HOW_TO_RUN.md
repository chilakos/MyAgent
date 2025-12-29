# How to Interact with the Chatbot (Step 1)

## Current Status

You have the **LLM abstraction layer** built and ready. You can test it in 3 ways:

---

## Option 1: Mock Demo (Recommended - No Setup Required!)

**No API or Ollama needed.** Shows simulated conversation with mocked responses.

```bash
cd c:\Users\george\MyAgent
C:\Users\george\MyAgent\venv\Scripts\python.exe examples/demo_automated.py
```

**Output**: Simulated 3-message conversation with mock LLM

---

## Option 2: Interactive Mock Demo

**No API or Ollama needed.** Type your own messages, get mock responses.

```bash
C:\Users\george\MyAgent\venv\Scripts\python.exe examples/demo_mock.py
```

**Usage**:
```
You: Hello!
Assistant: I'm a mock chatbot. How can I help you?
You: What is Python?
Assistant: [Mock response]
You: quit
Goodbye!
```

---

## Option 3: Real LLM Demo (Requires Setup)

### For Ollama (Local Model):

1. Install Ollama: https://ollama.ai
2. Start Ollama: `ollama serve`
3. Pull a model: `ollama pull mistral`
4. Run the demo:
   ```bash
   C:\Users\george\MyAgent\venv\Scripts\python.exe examples/demo.py
   ```

### For OpenAI (Cloud):

1. Get an API key from https://openai.com
2. Create `.env` file (copy from `.env.example`)
3. Add your API key: `OPENAI_API_KEY=sk-...`
4. Edit `examples/demo.py` line 12, change:
   ```python
   if settings.llm_provider == "ollama":
   ```
   to:
   ```python
   if settings.llm_provider == "openai":  # or set LLM_PROVIDER=openai in .env
   ```
5. Run the demo:
   ```bash
   C:\Users\george\MyAgent\venv\Scripts\python.exe examples/demo.py
   ```

---

## Run Tests

Verify everything works with unit tests (18 tests):

```bash
C:\Users\george\MyAgent\venv\Scripts\python.exe -m pytest tests/unit/test_llm.py -v
```

**Expected Output**: `18 passed ✅`

---

## Code Examples

### Using the LLM abstraction in your own code:

```python
from src.core.llm import create_llm_provider
from langchain_core.messages import HumanMessage, AIMessage

# Create provider
llm = create_llm_provider(
    provider_type="ollama",
    ollama_base_url="http://localhost:11434",
    ollama_model="mistral"
)

# Initialize
llm.initialize()

# Chat
messages = [HumanMessage(content="Hello!")]
response = llm.chat(messages, temperature=0.7)
print(response)

# Get info
info = llm.get_model_info()
print(info)
```

---

## Demo Features

The automated demo shows:
- ✅ Creating an LLM provider
- ✅ Maintaining conversation history
- ✅ Multiple turn interactions
- ✅ Mocked responses (no API calls)

---

## What's Next?

After reviewing the demo, you can:

1. **Merge to develop** (simulate PR approval):
   ```bash
   git checkout develop
   git merge feature/llm-setup
   ```

2. **Start Step 2** (CLI chatbot with memory):
   ```bash
   git checkout -b feature/cli-chatbot
   ```

3. **Continue building** with FastAPI, RAG, etc.

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'src'"**
- Make sure you're running from the project root (`c:\Users\george\MyAgent`)

**Demo shows errors about missing LangChain packages**
- Run: `C:\Users\george\MyAgent\venv\Scripts\python.exe -m pip install langchain-ollama langchain-openai`

**Want to use real Ollama but it won't connect?**
- Verify Ollama is running: `ollama serve`
- Check it's on `http://localhost:11434`
- Verify model exists: `ollama list` (should show `mistral`)
