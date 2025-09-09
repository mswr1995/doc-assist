# Use Python slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --no-dev

# Copy source code
COPY src/ ./src/

# Create directories for data and vector DB
RUN mkdir -p /app/data /app/chroma_db

# Set environment variables with defaults
ENV PYTHONPATH=/app
ENV UPLOAD_DIR=/app/data
ENV VECTOR_DB_PATH=/app/chroma_db
ENV API_HOST=0.0.0.0
ENV API_PORT=8000
ENV API_RELOAD=false

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the application
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]