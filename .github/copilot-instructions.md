<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Local Chatbot Project Instructions

## Project Overview

Building a local Python chatbot with Git workflow practice (branching, PRs) and comprehensive unit testing. Features dual LLM support (Ollama local + OpenAI API), CLI chat interface, FastAPI web API, and conversation memory.

## Development Practices

- **Git Workflow**: Feature branches → develop branch → PRs to develop → merge to main
- **Testing**: Unit tests with mocking (fast), integration tests marked as slow
- **Code Structure**: LLM abstraction layer for easy provider swapping

## Current Status

- [x] Project structure and testing foundation
- [ ] LLM abstraction (Ollama + OpenAI) - feature/llm-setup
- [ ] CLI chatbot with memory - feature/cli-chatbot
- [ ] FastAPI web API - feature/api-endpoints
- [ ] RAG support - feature/rag-support

## Key Technologies

- **LLM**: Ollama (local), OpenAI (optional)
- **Framework**: LangChain
- **API**: FastAPI
- **Testing**: pytest, pytest-mock
- **Vector DB**: ChromaDB (planned)
