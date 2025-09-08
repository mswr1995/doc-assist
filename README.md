# DocAssist

A backend-only intelligent document assistant built with Python, FastAPI, and local LLM integration. Upload documents and ask questions - get answers with source citations.

## Project Goals
Learning-focused RAG (Retrieval-Augmented Generation) system to demonstrate:
- Backend API development
- Document processing and vector storage
- Local LLM integration
- Modern Python development practices

## Tech Stack
- **Python 3.12** with UV dependency management
- **FastAPI** for RESTful APIs
- **ChromaDB** for vector storage
- **Ollama** for local LLM inference
- **Docker** for containerization

## Project Structure
```
src/
├── api/          # FastAPI routes
├── core/         # Business logic (documents, RAG, vector store)
├── llm/          # LLM integration
├── models/       # Pydantic schemas
├── config.py     # Configuration
└── main.py       # App entry point
```

## Getting Started
```bash
# Install dependencies
uv sync

# Run the application
make run

# Or with Docker
docker build -t docassist .
docker run -p 8000:8000 docassist
```

## Development Status
- [x] Project setup and structure
- [x] Document utilities
- [x] Containerization
- [x] Text processing
- [ ] Vector store integration
- [ ] LLM integration
- [ ] API endpoints

---
*This project is built for learning and demonstration purposes.*
