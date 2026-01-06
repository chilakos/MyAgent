# Local Chatbot/Personal Agent

A local Python AI agent built with LangChain, Ollama/OpenAI/Gemini, and SQLite. Features conversation memory, habit tracking, and integrated daily check-ins for personal productivity.

## ✨ Features

- **Multi-LLM Support**: Ollama (local, free, offline) | OpenAI (cloud, production) | Gemini (cloud)
- **Conversation Memory**: SQLite-based persistent conversations with 6 conversation types
- **Daily Habit Tracking**: Track 5 habits with completion %, streaks, and weekly/monthly reports
- **PDF Agent**: Autonomous PDF operations (merge, split, extract text, rotate pages) with natural language interface
- **Interactive CLI**: Chat interface with auto-save and conversation management
- **Comprehensive Tests**: 30+ unit tests for core functionality
- **FastAPI Web API** (Planned): REST endpoints for chat and habit tracking

## 📊 Current Features

### Conversation Types
- `daily_checkin` - Daily reflection and goals
- `weekly_review` - Weekly progress assessment
- `routine` - Habit and routine tracking
- `finance` - Budget and expense discussion
- `goals` - Long-term goal planning
- `general` - Open conversations

### Habit Tracking
Track completion with visual progress:
```
✓ 45 min workout
   4/7 days | ████████░░ 71%
   🔥 2 day streak
```

Habits are configured and easily customizable:
1. 45 min workout (or minimum 20 min)
2. 10 min walk after meals
3. Eat clean; no junk
4. Last food ≥4 hrs before bed
5. 30 min reading

### PDF Agent
Autonomous PDF operations with AI:
```bash
python examples/demo_pdf_agent.py
```

Capabilities:
- **Merge PDFs**: Combine multiple documents into one
- **Split PDFs**: Divide by page count or custom ranges
- **Extract Text**: Advanced text extraction with pdfplumber
- **Extract Pages**: Create new PDFs from specific pages
- **Rotate Pages**: Rotate by 90/180/270 degrees
- **Get Metadata**: Retrieve PDF info (author, page count, etc.)

Natural language interface:
```
You: Merge report1.pdf and report2.pdf into final.pdf
Agent: Successfully merged 2 PDFs. Output: ./pdf_workspace/final.pdf
```

See [PDF Agent Documentation](docs/PDF_AGENT.md) for complete guide.

## 📁 Project Structure

```
.
├── src/
│   ├── core/
│   │   ├── llm.py           # LLM abstraction (Ollama/OpenAI/Gemini)
│   │   ├── memory.py        # SQLite conversation & habit persistence
│   │   ├── habits.py        # Habit tracker configuration
│   │   └── config.py        # Settings and environment
│   └── agents/
│       ├── pdf_agent.py     # PDF operations agent
│       └── pdf_tools.py     # LangChain PDF tools
├── examples/
│   ├── demo.py              # Interactive chatbot with habits
│   └── demo_pdf_agent.py    # PDF agent demo
├── tests/unit/
│   ├── test_memory.py       # Memory system tests
│   └── test_pdf_agent.py    # PDF agent tests (30 tests)
├── docs/
│   └── PDF_AGENT.md         # PDF agent documentation
├── data/
│   └── conversations.db     # SQLite database
└── .env                     # Configuration (Ollama/OpenAI/Gemini)
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
cd MyAgent
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
```

### 2. Choose Your LLM

**Option A: Local (Ollama - Recommended for learning)**
```bash
# Install Ollama from https://ollama.ai
# Pull a model
ollama pull mistral

# In another terminal, start Ollama server
ollama serve

# Run agent
python examples/demo.py
```

**Option B: OpenAI (Production ready)**
```bash
# Set in .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

python examples/demo.py
```

**Option C: Gemini (Cloud)**
```bash
# Set in .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.0-flash

python examples/demo.py
```

### 3. Use the Agent

```
You: hello
Assistant: [Response from LLM]

Available commands:
  'habits'      → Log daily habits
  'stats'       → View weekly habit summary
  'new <type>'  → Start new conversation (daily_checkin, weekly_review, etc)
  'list'        → Show recent conversations
  'quit'        → Exit
```

## 💾 Database Schema

### conversations table
- `id` (UUID) - Unique conversation ID
- `type` - Conversation type (daily_checkin, routine, etc)
- `title` - User-friendly title
- `messages` - JSON array of HumanMessage/AIMessage
- `created_at`, `updated_at` - Timestamps
- `metadata` - Custom metadata (JSON)

### habit_logs table
- `id` (UUID) - Unique log entry ID
- `habit_id` - Reference to habit
- `logged_date` - YYYY-MM-DD
- `completed` - Boolean
- `notes` - Optional user notes
- `created_at` - Timestamp

## 📊 Testing

```bash
# Run all tests
pytest

# Unit tests only
pytest tests/unit/

# Test specific module
pytest tests/unit/test_pdf_agent.py -v

# Test coverage
pytest --cov=src tests/

# Run specific test
pytest tests/unit/test_memory.py::TestConversationManager::test_create_conversation
```

Current: **30+ passing tests** for memory and PDF agent modules

## 🔄 Git Workflow

- **main**: Production-ready
- **develop**: Integration branch
- **feature/***: Feature branches

All changes go through `develop` branch before merging to `main`.

## 🗺️ Roadmap

- ✅ SQLite memory system with 6 conversation types
- ✅ LLM abstraction (Ollama, OpenAI, Gemini)
- ✅ Daily habit tracking with statistics
- ✅ Interactive CLI with auto-save
- ✅ PDF Agent with autonomous operations
- 🔄 Weekly/monthly reports with AI insights
- 🔄 FastAPI web interface
- 🔄 Goal tracking and progress graphs
- 🔄 Financial tracking integration

## 📝 Configuration

Create `.env` file in project root:

```bash
# LLM Provider (ollama, openai, or gemini)
LLM_PROVIDER=ollama

# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# OpenAI (optional)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Gemini (optional)
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.0-flash

# API Server
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
```

## 🛠️ Technologies

- **LangChain**: LLM framework
- **Ollama**: Local inference
- **SQLite3**: Lightweight database
- **Pydantic**: Data validation
- **pytest**: Testing framework
- **FastAPI**: REST API (planned)

## 📄 License

MIT
