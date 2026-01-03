## Starting Ollama

Ollama needs to be running for the local agent to work.

### On Windows:

1. **Install Ollama** (if not already installed):
   - Download from https://ollama.ai
   - Install it

2. **Start Ollama**:
   ```powershell
   ollama serve
   ```
   This will start the Ollama server at http://localhost:11434

3. **Pull the model** (if not already downloaded):
   Open a new terminal/PowerShell and run:
   ```powershell
   ollama pull mistral
   ```
   This downloads the Mistral model (~7GB, takes a few minutes)

4. **Test it**:
   ```powershell
   cd c:\Users\george\MyAgent
   python test_ollama.py
   ```

Once Ollama is running in the background, you can start the agent:
```powershell
python examples/demo.py
```

## Why Ollama?

✓ Instant responses (2-5 seconds vs 30-60 for cloud APIs)
✓ Free (runs locally)
✓ Privacy (data doesn't leave your computer)
✓ No API keys needed
✓ Works offline

## Current Setup

- **Provider**: Ollama (local)
- **Model**: Mistral 7B
- **Base URL**: http://localhost:11434
- **Memory**: SQLite database (data/conversations.db)
