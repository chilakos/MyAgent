# Setup Guide

## Prerequisites

You need to install:

1. **Python 3.9+** - Download from https://www.python.org/downloads/
   - During installation, **CHECK "Add Python to PATH"**
   
2. **Git** - Already installed! (verified at C:\Program Files\Git\cmd)

3. **Ollama** (Optional, for local LLM) - Download from https://ollama.ai
   - After installation, run: `ollama pull mistral`

## Setup Steps

Once Python is installed:

```powershell
# Navigate to project
cd c:\Users\george\MyAgent

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# Install dependencies (dev includes test dependencies)
pip install -r requirements-dev.txt

# Run tests to verify setup
pytest

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings (OpenAI key if using it)
```

## Verify Installation

After setup, run:

```powershell
# Run all tests
pytest -v

# Run only unit tests (fast)
pytest -m "not slow" -v

# Run with coverage
pytest --cov=src --cov-report=html
```

## Next Steps

1. **Install Python** and activate virtual environment
2. **Install dependencies** with pip
3. **Start Step 1**: Create feature branch `feature/llm-setup` and begin implementing LLM abstraction

See README.md for full project overview.
