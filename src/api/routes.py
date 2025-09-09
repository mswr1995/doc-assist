from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
import os

from src.core.rag import RAGEngine
from src.config import config
from src.models.schemas import (
    DocumentUploadResponse,
    QuestionRequest,
    QuestionResponse,
    DocumentListResponse,
    HealthResponse
)


# create router for our endpoints
router = APIRouter()

# global RAG engine instance
rag_engine = None

def get_rag_engine():
    """get or create RAG engine instance"""
    global rag_engine
    if rag_engine is None:
        try:
            rag_engine = RAGEngine()
        except Exception as e:
            raise HTTPException(
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
                detail = f"Failed to initialize RAG engine: {str(e)}"
            )
        
    return rag_engine
        

@router.get("/health", response_model = HealthResponse)
async def health_check():
    """
    Check system health and status.
    Returns information about LLM connection, documents, etc.
    """
    try:
        rag = get_rag_engine()
        status_info = rag.get_system_status()

        return HealthResponse(
            system_ready = status_info.get("system_ready", False),
            llm_connected = status_info.get("llm_connected", False),
            document_system_ready = status_info.get("document_system_ready", False),
            total_documents = status_info.get("total_documents", 0),
            total_chunks = status_info.get("total_chunks", 0),
            model_name = status_info.get("model_name", "unknown")
        )
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Health check failed: {str(e)}"
        )
    

@router.post("/documents/upload", response_model = DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document.
    Supports PDF, DOCX, TXT files.
    """
    # use config for file validation
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in config.SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"Unsupported file type. Allowed: {', '.join(config.SUPPORTED_EXTENSIONS)}"
        )
    
    try:
        # read file content
        content = await file.read()

        # process document
        rag = get_rag_engine()
        result = rag.upload_and_process_document(file.filename, content)

        if result["status"] != "success":
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = f"Failed to process document: {result.get('error', 'Unknown error')}"
            )
        
        return DocumentUploadResponse(
            status = result["status"],
            filename = result["filename"],
            message = result["message"],
            num_chunks = result["num_chunks"],
            file_path = result["file_path"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Upload failed: {str(e)}"
        )
    

@router.get("/documents/", response_model = DocumentListResponse)
async def list_documents():
    """
    Get list of all uploaded and processed documents.
    """
    try:
        rag = get_rag_engine()
        result = rag.list_available_documents()

        if result["status"] != "success":
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = "Failed to list documents"
            )
        
        return DocumentListResponse(
            status = result["status"],
            documents = result["documents"],
            file_count = result["file_count"],
            vector_chunk_count = result["vector_chunk_count"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Failed to list documents: {str(e)}"
        )


@router.post("/documents/query", response_model = QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about uploaded documents.
    Returns AI-generated answer with source citations.
    """
    try:
        rag = get_rag_engine()
        result = rag.ask_question(
            question = request.question,
            n_chunks = request.max_chunks
        )

        return QuestionResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result["sources"],
            success=result["success"],
            chunks_found=result["chunks_found"],
            model_used=result["model_used"],
            error=result.get("error")
        )
    
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Question processing failed: {str(e)}"
        )