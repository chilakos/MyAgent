# Setup: Using Real LLM

## Option A: Ollama (Local - Recommended for Learning)

### Step 1: Install Ollama
1. Go to https://ollama.ai
2. Download for Windows
3. Run the installer
4. Follow the installation prompts
5. **Restart your computer** after installation

### Step 2: Start Ollama
After restarting, Ollama runs in the background automatically. To verify:

```powershell
# Test if Ollama is running
curl http://localhost:11434/api/tags
```

You should see a response (might be empty tags initially).

### Step 3: Pull a Model
Open PowerShell and run:

```powershell
ollama pull mistral
```

This downloads Mistral 7B (4GB, takes a few minutes).

### Step 4: Run the Demo
```powershell
cd c:\Users\george\MyAgent
C:\Users\george\MyAgent\venv\Scripts\python.exe examples/demo.py
```

You can now chat with a real local model!

---

## Option B: OpenAI (Cloud - Production Ready)

### Step 1: Get API Key
1. Go to https://platform.openai.com/api/keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### Step 2: Configure .env
1. Copy `.env.example` → `.env`
2. Edit `.env` and add your key:
   ```
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-your-actual-key-here
   OPENAI_MODEL=gpt-4o-mini
   ```

### Step 3: Run the Demo
```powershell
cd c:\Users\george\MyAgent
C:\Users\george\MyAgent\venv\Scripts\python.exe examples/demo.py
```

You can now chat with GPT-4!

---

## Troubleshooting

### Ollama Connection Error
```
Error initializing LLM: [Errno 10061] No connection could be made
```
**Solution**: Ollama isn't running. After installation, restart Windows or start Ollama manually.

### Model Not Found
```
Error: model 'mistral' not found
```
**Solution**: Run `ollama pull mistral` to download it.

### OpenAI Auth Error
```
Error initializing LLM: Unauthorized
```
**Solution**: Check your API key in `.env` file (no spaces, starts with `sk-`)

---

## Cost Comparison

| Provider | Cost | Speed | Privacy |
|----------|------|-------|---------|
| **Ollama** | Free | Fast (local) | Local only |
| **OpenAI** | ~$0.15 per 1K tokens | Medium (cloud) | Sent to OpenAI |

For a typical 100-message conversation:
- **Ollama**: $0
- **OpenAI**: ~$0.05

---

## Which Should I Choose?

**Choose Ollama if:**
- ✅ You want free, unlimited usage
- ✅ You value privacy
- ✅ You're learning/experimenting
- ✅ You have 8GB+ RAM

**Choose OpenAI if:**
- ✅ You want highest quality responses
- ✅ You're building production
- ✅ You want latest models (GPT-4)
- ✅ You don't want to manage local infrastructure

---

## Next Steps

1. Choose Ollama or OpenAI
2. Follow the setup above
3. Run: `C:\Users\george\MyAgent\venv\Scripts\python.exe examples/demo.py`
4. Chat with a real AI!
