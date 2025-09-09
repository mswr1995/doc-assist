# DocAssist

A production-ready, backend-only intelligent document assistant implementing a complete RAG (Retrieval-Augmented Generation) system. Upload documents and get AI-powered answers with source citations using only local, open-source tools.

## Features

**Document Processing**
- Support for PDF, DOCX, and TXT files
- Intelligent text chunking with context preservation
- Automatic text cleaning and normalization

**Semantic Search**
- ChromaDB vector storage for fast similarity search
- Automatic embedding generation
- Metadata tracking for source citations

**Local LLM Integration**
- Ollama integration for private, offline inference
- Custom prompt engineering for accurate responses
- Anti-hallucination through strict source citation

**Production Architecture**
- Modular, testable codebase
- Comprehensive test suite
- Docker containerization
- RESTful API design

## Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/doc-assist.git
cd doc-assist

# Install dependencies
uv sync

# Run tests
make test

# Start the application
make run

# Or with Docker
docker build -t docassist .
docker run -p 8000:8000 docassist
```

## Architecture

```
src/
├── api/              # FastAPI routes and request handling
├── core/             # Core business logic
│   ├── document_utils.py      # File operations
│   ├── text_processor.py     # Text extraction and chunking
│   ├── vector_store.py       # ChromaDB integration
│   ├── document_processor.py # Pipeline orchestration
│   └── rag.py               # Retrieval-augmented generation
├── llm/              # Local LLM integration
├── models/           # Pydantic schemas and data models
├── config.py         # Configuration management
└── main.py          # Application entry point
```

## API Endpoints

```http
POST /documents/upload    # Upload and process documents
GET  /documents/         # List uploaded documents
POST /documents/query    # Ask questions about documents
GET  /health            # Health check endpoint
```

## Development Status

**Phase 1: Core Infrastructure** ✅
- [x] Document file operations
- [x] Text processing and chunking
- [x] Vector storage integration
- [x] Comprehensive unit testing

**Phase 2: Integration Layer** 🚧
- [ ] Document processing pipeline
- [ ] Configuration management
- [ ] Integration testing

**Phase 3: AI Integration** ⏳
- [ ] Ollama LLM connection
- [ ] RAG implementation
- [ ] Prompt optimization

**Phase 4: API Layer** ⏳
- [ ] FastAPI endpoints
- [ ] Request/response schemas
- [ ] API documentation

**Phase 5: Production Ready** ⏳
- [ ] Error handling and logging
- [ ] Performance monitoring
- [ ] Deployment optimization

## Tech Stack

- **Python 3.12** - Core language
- **FastAPI** - Web framework
- **ChromaDB** - Vector database
- **Ollama** - Local LLM runtime
- **UV** - Dependency management
- **Docker** - Containerization
- **Pytest** - Testing framework

## Requirements

- Python 3.12+
- Docker (optional)
- 4GB+ RAM for LLM inference

## Contributing

This project follows test-driven development and modular architecture principles. Each component is independently testable and follows single responsibility patterns.

## License

MIT License - See LICENSE file for details.

---

*Built for learning modern RAG architecture and production backend development.*
