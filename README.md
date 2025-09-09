# DocAssist

A complete intelligent document assistant built with modern Python architecture. Upload documents (PDF, DOCX, TXT) and ask questions to get AI-powered answers with source citations. Everything runs locally using open-source tools - no external APIs required.

## What This System Does

DocAssist solves the problem of extracting information from large document collections. Instead of manually searching through files, you upload documents and ask natural language questions. The system finds relevant content and generates accurate answers with source citations.

**Core Workflow:**
1. Upload documents via REST API
2. System extracts text and creates searchable chunks
3. Stores content in vector database for semantic search
4. Ask questions via API
5. System finds relevant chunks and generates contextual answers
6. Returns answers with source document citations

## Technical Features

### Document Processing Engine
- **Multi-format support**: PDF, DOCX, and TXT files
- **Smart text extraction**: Handles complex layouts and formatting
- **Intelligent chunking**: Splits text while preserving context and meaning
- **Text normalization**: Cleans and standardizes content for better search

### Vector Search System
- **ChromaDB integration**: High-performance vector database
- **Semantic search**: Find content by meaning, not just keywords
- **Automatic embeddings**: Converts text to mathematical representations
- **Metadata tracking**: Maintains document source information for citations

### Local AI Integration
- **Ollama LLM server**: Private, offline large language model
- **Custom prompts**: Engineered for accurate, source-based responses
- **Anti-hallucination**: Strict requirements for source-backed answers
- **Multiple model support**: Compatible with various Ollama models

### Production-Ready Architecture
- **Modular design**: Independent, testable components
- **Configuration management**: Environment-based settings
- **Error handling**: Comprehensive exception management
- **API documentation**: Auto-generated OpenAPI/Swagger docs
- **Docker containerization**: Complete deployment solution

## Installation and Setup

### Prerequisites
- Python 3.12 or higher
- 8GB RAM minimum (for LLM inference)
- Docker (optional but recommended)
- Git

### Method 1: Local Development Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd doc-assist

# Install UV package manager (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync

# Install and start Ollama
# On Windows: Download from https://ollama.com
# On macOS: brew install ollama
# On Linux: curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve

# In another terminal, pull the language model
ollama pull llama3.2:1b

# Start the development server
make run
# Or manually: uv run uvicorn src.main:app --reload

# Visit the API documentation
open http://localhost:8000/docs
```

### Method 2: Docker Setup (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd doc-assist

# Start complete system (DocAssist + Ollama)
make docker-setup

# This command will:
# 1. Build the Docker images
# 2. Start both containers
# 3. Download the language model
# 4. Configure networking between services

# Visit the API documentation
open http://localhost:8000/docs
```

## Project Structure

```
doc-assist/
├── src/                          # Application source code
│   ├── api/                      # REST API layer
│   │   └── routes.py             # FastAPI endpoint definitions
│   ├── core/                     # Business logic layer
│   │   ├── document_utils.py     # File operations and storage
│   │   ├── text_processor.py     # Text extraction and chunking
│   │   ├── vector_store.py       # ChromaDB vector database interface
│   │   ├── document_processor.py # Document processing pipeline
│   │   └── rag.py               # Retrieval-augmented generation engine
│   ├── llm/                      # Language model integration
│   │   └── llm_utils.py         # Ollama client and prompt management
│   ├── models/                   # Data models and schemas
│   │   └── schemas.py           # Pydantic request/response models
│   ├── config.py                # Application configuration
│   └── main.py                  # FastAPI application entry point
├── tests/                       # Test suite
├── data/                        # Document storage (created at runtime)
├── chroma_db/                   # Vector database storage (created at runtime)
├── Dockerfile                   # Docker container definition
├── docker-compose.yml           # Multi-container orchestration
├── pyproject.toml              # Project dependencies and metadata
├── Makefile                    # Build and development commands
└── README.md                   # This file
```

## API Documentation

The system provides a RESTful API with the following endpoints:

### Health Check
```http
GET /api/v1/health
```
Returns system status including LLM connection and document count.

### Document Upload
```http
POST /api/v1/documents/upload
Content-Type: multipart/form-data

file: <document file>
```
Uploads and processes a document. Supported formats: PDF, DOCX, TXT.

**Response:**
```json
{
  "status": "success",
  "filename": "document.pdf",
  "message": "Document processed successfully",
  "num_chunks": 8,
  "file_path": "./data/document.pdf"
}
```

### List Documents
```http
GET /api/v1/documents/
```
Returns list of all uploaded and processed documents.

### Question Answering
```http
POST /api/v1/documents/query
Content-Type: application/json

{
  "question": "What is the main topic of the document?",
  "max_chunks": 5
}
```

**Response:**
```json
{
  "question": "What is the main topic of the document?",
  "answer": "Based on the provided documents, the main topic is...",
  "sources": ["document.pdf"],
  "success": true,
  "chunks_found": 3,
  "model_used": "llama3.2:1b",
  "error": null
}
```

## Configuration

The system uses environment variables for configuration. Create a `.env` file in the project root:

```bash
# File Storage
UPLOAD_DIR=./data
VECTOR_DB_PATH=./chroma_db

# LLM Settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b

# RAG Settings
MAX_CHUNKS=5
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=*

# LLM Generation Settings
LLM_TEMPERATURE=0.1
LLM_TOP_P=0.9
LLM_MAX_TOKENS=500
```

## Development Commands

```bash
# Install dependencies
make install

# Run development server with auto-reload
make run

# Start complete Docker environment
make docker-setup

# Stop Docker containers
make docker-down

# Clean temporary files
make clean
```

## Testing the System

### 1. Upload a Document
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@example.pdf"
```

### 2. Ask a Question
```bash
curl -X POST "http://localhost:8000/api/v1/documents/query" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?", "max_chunks": 5}'
```

### 3. Using the Web Interface
Visit `http://localhost:8000/docs` for an interactive API interface where you can:
- Upload documents through a web form
- Test queries with a built-in interface
- View API documentation and examples

## Technical Architecture

### Document Processing Pipeline
```
File Upload → Text Extraction → Text Cleaning → Chunking → Vector Embedding → Storage
```

### Question Answering Pipeline
```
User Question → Vector Search → Relevant Chunks → LLM Processing → Contextualized Answer
```

### Technology Stack Details
- **FastAPI**: Modern web framework with automatic API documentation
- **ChromaDB**: Vector database optimized for similarity search
- **Ollama**: Local LLM runtime supporting multiple models
- **UV**: Fast Python package manager
- **Docker**: Containerization for consistent deployment
- **Pydantic**: Data validation and serialization

## Performance Considerations

### System Requirements
- **Memory**: 8GB minimum (4GB for LLM, 2GB for vector database, 2GB for system)
- **Storage**: 1GB for models, additional space for documents and embeddings
- **CPU**: Multi-core processor recommended for faster processing

### Optimization Tips
- Use smaller models (llama3.2:1b) for faster responses on limited hardware
- Adjust chunk size based on document types and query patterns
- Monitor vector database size and consider cleanup for production use
- Use Docker for consistent performance across environments

## Troubleshooting

### Common Issues

**Ollama Connection Failed**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama service
ollama serve
```

**Model Not Found**
```bash
# List available models
ollama list

# Pull required model
ollama pull llama3.2:1b
```

**Memory Issues**
- Try smaller model: `OLLAMA_MODEL=llama3.2:1b`
- Reduce chunk size: `CHUNK_SIZE=500`
- Reduce max chunks: `MAX_CHUNKS=3`

**Docker Issues**
```bash
# Clean Docker system
make docker-down
docker system prune -f

# Rebuild from scratch
make docker-setup
```

## Future Development Roadmap

### Database Integration
**What:** Add PostgreSQL for user management and metadata storage
**Why:** Enable multi-user support, document permissions, and usage analytics
**Implementation:**
- User authentication and authorization
- Document access control
- Chat history persistence
- Usage statistics and analytics

### Advanced RAG Features
**What:** Enhance retrieval and generation capabilities
**Options:**
- Hybrid search (keyword + semantic)
- Query expansion and reformulation
- Multi-document conversation threads
- Document summarization endpoints
- Custom embedding models for domain-specific content

### Frontend Development
**What:** Build user-friendly web interface
**Options:**
- React/Vue.js web application
- Real-time chat interface
- Document preview and highlighting
- Visual analytics dashboard
- Mobile-responsive design

### Production Features
**What:** Enterprise-ready capabilities
**Options:**
- Horizontal scaling with load balancers
- Advanced monitoring and logging
- Automated testing and CI/CD
- Performance metrics and alerting
- Data backup and recovery systems

### Advanced Document Processing
**What:** Support for more complex document types
**Options:**
- Image extraction from PDFs with OCR
- Table and chart processing
- PowerPoint and Excel support
- Markdown and HTML processing
- Document version tracking

### Language and Localization
**What:** Multi-language support
**Options:**
- Multilingual embedding models
- Language detection and routing
- Translation capabilities
- Locale-specific formatting
- International character support

### Integration Capabilities
**What:** Connect with external systems
**Options:**
- API integrations with cloud storage (S3, Google Drive)
- Email processing and attachment extraction
- Webhook support for automation
- Integration with existing document management systems
- Export capabilities (JSON, CSV, PDF reports)

## Contributing

This project follows modern Python development practices:
- Type hints throughout the codebase
- Modular architecture with clear separation of concerns
- Comprehensive error handling and logging
- Environment-based configuration management
- Docker-first deployment strategy

To contribute:
1. Fork the repository
2. Create a feature branch
3. Follow the existing code style and patterns
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request

## License

MIT License - see LICENSE file for full details.

This project is designed for learning modern backend development, RAG architecture, and production system design. It demonstrates real-world patterns and practices used in enterprise document processing
