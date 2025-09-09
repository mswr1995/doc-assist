import os
from pathlib import Path
from typing import Optional

class Config:
    """
    Application configuration management.
    Uses environment variables with sensible defaults.
    """
    
    # File and Storage Settings
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "./data"))
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./chroma_db")
    
    # LLM Settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    
    # RAG Settings
    MAX_CHUNKS: int = int(os.getenv("MAX_CHUNKS", "5"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # API Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    
    # CORS Settings
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Supported File Types
    SUPPORTED_EXTENSIONS: set = {".pdf", ".docx", ".txt"}
    
    # LLM Generation Settings
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_TOP_P: float = float(os.getenv("LLM_TOP_P", "0.9"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "500"))
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        Path(cls.VECTOR_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_display_config(cls) -> dict:
        """Get configuration for display/debugging purposes."""
        return {
            "upload_dir": str(cls.UPLOAD_DIR),
            "vector_db_path": cls.VECTOR_DB_PATH,
            "ollama_url": cls.OLLAMA_BASE_URL,
            "ollama_model": cls.OLLAMA_MODEL,
            "max_chunks": cls.MAX_CHUNKS,
            "chunk_size": cls.CHUNK_SIZE,
            "api_port": cls.API_PORT,
            "supported_files": list(cls.SUPPORTED_EXTENSIONS)
        }

# Create singleton instance
config = Config()

# Database Configuration (for future use)
class DatabaseConfig:
    """
    Database configuration - to be implemented when we add user management,
    chat history, and other persistent data features.
    
    Future features:
    - User authentication and management
    - Chat history persistence  
    - Document access control
    - Usage analytics
    - System audit logs
    """
    
    # Placeholder for future database settings
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", None)
    
    @classmethod
    def is_enabled(cls) -> bool:
        """Check if database features are enabled."""
        return cls.DATABASE_URL is not None

# Note: Database features will be added in future versions
db_config = DatabaseConfig()