# Changelog

All notable changes to the Aether AI Backend project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial Python Flask backend setup
- SQLAlchemy models for Chat, Message, Document, Suggestion
- LangChain integration with Ollama for local LLM support
- SSE streaming support for chat responses
- Multi-model support with model selection API
- Flask blueprints for chat, document, history, and health endpoints
- Authentication middleware for Next.js session verification
- LangChain tools: weather, create-document, update-document, request-suggestions
- Development tooling: pylint, black, pytest
- Makefile with common development commands
- Alembic database migrations
- RAG, voice, and research mode service scaffolds

### Changed
- Migrated from Vercel AI SDK + xAI/Grok to local Ollama models
- Moved chat and document logic from Next.js to Python backend

### Deprecated
- None

### Removed
- Third-party AI API dependencies (xAI, Vercel AI Gateway)

### Fixed
- None

### Security
- Added backend API key authentication between frontend and backend

