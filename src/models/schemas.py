from pydantic import BaseModel
from typing import List, Optional


class DocumentUploadResponse(BaseModel):
    """Response for document upload"""
    status: str
    filename: str
    message: str
    num_chunks: int
    file_path: str


class QuestionRequest(BaseModel):
    """Request for asking a question"""
    question: str
    max_chunks: Optional[int] = 5


class QuestionResponse(BaseModel):
    """Response for question answering"""
    question: str
    answer: str
    sources: List[str]
    success: bool
    chunks_found: int
    model_used: str
    error: Optional[str] = None


class DocumentListResponse(BaseModel):
    """Response for listing documents"""
    status: str
    documents: List[str]
    file_count: int
    vector_chunk_count: int


class HealthResponse(BaseModel):
    """Response for health check"""
    system_ready: bool
    llm_connected: bool
    document_system_ready: bool
    total_documents: int
    total_chunks: int
    model_name: str