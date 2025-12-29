# Local Chatbot/Copilot

A local Python chatbot built with LangChain, Ollama/OpenAI, and FastAPI. This project is designed to practice Git workflows (branching, PRs) and build comprehensive unit tests.

## Features

- **Dual LLM Support**: Use Ollama locally (free, offline) or OpenAI API (production-ready)
- **CLI Chat Interface**: Simple command-line chatbot
- **FastAPI Web API**: REST API endpoints for chat
- **Conversation Memory**: Persistent conversation history
- **RAG Support** (Planned): Document retrieval and context injection
- **Comprehensive Tests**: Unit and integration tests with mocking

## Project Structure

```
.
├── src/
│   ├── core/           # LLM integration, config, embeddings
│   ├── api/            # FastAPI routes and models
│   ├── agents/         # Chatbot logic
│   └── utils/          # Helpers and logging
├── tests/
│   ├── unit/           # Fast, mocked unit tests
│   ├── integration/    # Slow, real API tests
│   └── conftest.py     # Shared fixtures
├── requirements.txt    # Core dependencies
├── requirements-dev.txt # Dev/test dependencies
└── pytest.ini          # Test configuration
```

## Setup

1. **Clone and enter the repo**
   ```bash
   cd MyAgent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Install Ollama (optional, for local model)**
   - Download from https://ollama.ai
   - Pull a model: `ollama pull mistral`
   - Keep Ollama running: `ollama serve`

## Usage

### Run Tests
```bash
# All tests
pytest

# Unit tests only (fast)
pytest -m "not slow"

# With coverage
pytest --cov=src --cov-report=html
```

### CLI Chatbot (coming in feature/cli-chatbot)
```bash
python -m src.cli.main
```

### FastAPI Server (coming in feature/api-endpoints)
```bash
uvicorn src.api.main:app --reload
```

## Git Workflow

This project practices Git branching and PR workflows:

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/*****: Individual feature branches

Create a feature branch, make changes, write tests, commit, and open a PR to `develop`.

## Testing Strategy

- **Unit Tests**: Mocked LLM calls, fast feedback
- **Integration Tests**: Marked with `@pytest.mark.slow`, real API calls
- **Coverage Target**: 70%+ on business logic

See [tests/conftest.py](tests/conftest.py) for shared fixtures.

## Roadmap

1. ✅ Project setup with testing foundation
2. 🔄 LLM abstraction (Ollama + OpenAI)
3. 🔄 CLI chatbot with memory
4. 🔄 FastAPI web API
5. 🔄 RAG with ChromaDB

## License

MIT
