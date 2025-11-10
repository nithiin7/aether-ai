# Aether AI Backend

Python Flask backend for Aether AI - A locally-hosted AI assistant using Ollama and LangChain.

## Features

- 🤖 **Local LLM Integration** - Ollama-powered models running locally
- 💬 **Real-time Chat** - SSE streaming for responsive conversations
- 🔄 **Multi-Model Support** - Switch between different Ollama models
- 📝 **Document Management** - Create and manage text, code, image, and sheet artifacts
- 🔧 **LangChain Tools** - Weather, document creation/editing, suggestions
- 🔐 **Session Authentication** - Integration with Next.js authentication
- 🗄️ **PostgreSQL Database** - Persistent storage with SQLAlchemy ORM
- 🚀 **Future-Ready** - Scaffolds for RAG, voice, and research modes

## Architecture

```
backend/
├── src/
│   ├── api/blueprints/     # Flask route handlers
│   ├── models/             # SQLAlchemy database models
│   ├── services/           # Business logic layer
│   │   ├── tools/          # LangChain tools
│   │   ├── llm_service.py
│   │   ├── chat_service.py
│   │   ├── rag_service.py (scaffold)
│   │   ├── voice_service.py (scaffold)
│   │   └── research_service.py (scaffold)
│   ├── config/             # Configuration
│   ├── utils/              # Utilities (auth, errors)
│   └── app.py              # Flask app factory
├── migrations/             # Alembic database migrations
└── tests/                  # Test suite
```

## Prerequisites

- Python 3.9+
- PostgreSQL
- Ollama (running locally on port 11434)

## Quick Start

### 1. Install Ollama

```bash
# macOS
brew install ollama
ollama serve

# Pull a model
ollama pull phi3:mini
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
make venv
source venv/bin/activate

# Install dependencies
make install-dev

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### 3. Database Setup

```bash
# Update DATABASE_URL in .env
# postgresql://user:password@localhost:5432/aether_ai

# Run migrations
make db-upgrade
```

### 4. Run Development Server

```bash
make dev
```

Server runs at `http://localhost:5000`

## Environment Variables

Create `.env` file with:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key
DEBUG=True

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/aether_ai

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_DEFAULT_MODEL=phi3:mini

# API Security
BACKEND_API_KEY=shared-secret-between-frontend-and-backend

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Logging
LOG_LEVEL=INFO
```

## Available Models

The backend supports multiple Ollama models:

- **phi3:mini** (3.8B) - Fast, great for testing
- **llama3.2:3b** (3B) - Efficient with good performance
- **llama3.2:11b-vision** (11B) - Multimodal with vision capabilities
- **qwen2.5:7b** (7B) - Multilingual with strong reasoning
- **mixtral:8x7b** (47B) - Powerful mixture-of-experts

Pull models with: `ollama pull <model-name>`

## API Endpoints

### Health & Models
- `GET /api/health` - Health check
- `GET /api/health/models` - List available models

### Chat
- `POST /api/chat` - Create/continue chat (SSE streaming)
- `DELETE /api/chat?id=<chat_id>` - Delete chat
- `GET /api/chat/<chat_id>/messages` - Get chat messages

### Documents
- `POST /api/document` - Create document
- `GET /api/document/<id>` - Get document
- `PUT /api/document/<id>` - Update document
- `DELETE /api/document/<id>` - Delete document
- `GET /api/document` - List documents

### History
- `GET /api/history` - Get user's chat history

### Suggestions
- `GET /api/suggestions/<document_id>` - Get document suggestions
- `POST /api/suggestions/<suggestion_id>/resolve` - Resolve suggestion

## Development Commands

```bash
# Development
make dev          # Run Flask dev server
make test         # Run tests with coverage
make lint         # Run pylint
make format       # Format code with black

# Database
make db-upgrade   # Apply migrations
make db-downgrade # Rollback one migration
make db-migrate msg='description'  # Create new migration

# Utilities
make changelog    # Generate CHANGELOG.md
make clean        # Remove cache files
```

## Authentication

The backend expects authentication via:

1. **Authorization header**: `Bearer <jwt-token>`
2. **X-User-Id header**: For development (user UUID)
3. **X-API-Key header**: Shared secret for frontend-backend communication

Example request:
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Authorization: Bearer <token>" \
  -H "X-API-Key: shared-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "id": "msg-123",
      "role": "user",
      "parts": [{"type": "text", "text": "Hello!"}]
    },
    "model_id": "phi3:mini"
  }'
```

## Testing

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_llm_service.py -v

# Run with coverage report
pytest --cov=src --cov-report=html
```

## Code Quality

The project uses:
- **Pylint** - Code linting (configured in `.pylintrc`)
- **Black** - Code formatting (100 char line length)
- **isort** - Import sorting
- **pytest** - Testing framework

## Database Migrations

```bash
# Create a new migration
make db-migrate msg='add user preferences table'

# Apply migrations
make db-upgrade

# Rollback last migration
make db-downgrade

# View migration history
alembic history
```

## Future Features (Scaffolds)

### RAG (Retrieval-Augmented Generation)
- Document ingestion from PDFs, DOCX, TXT
- Vector embeddings with sentence-transformers
- ChromaDB/FAISS for vector storage
- Semantic search and context retrieval

### Voice Chat
- Speech-to-text with Whisper
- Text-to-speech with Coqui TTS or Bark
- Real-time streaming
- Multi-language support

### Research Mode
- Multi-step reasoning with LangChain agents
- Web search integration
- Document analysis and summarization
- Citation tracking and source verification

## Troubleshooting

### Ollama Connection Issues
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready

# Verify connection string in .env
# Format: postgresql://user:password@host:port/database
```

### Port Already in Use
```bash
# Find process using port 5000
lsof -ti:5000

# Kill process
kill -9 <PID>
```

## Contributing

1. Create a feature branch
2. Make changes with tests
3. Run `make lint` and `make format`
4. Run `make test` to verify
5. Update CHANGELOG.md
6. Submit pull request

## License

See LICENSE file in project root.

## Support

For issues and questions, please open an issue on the repository.

