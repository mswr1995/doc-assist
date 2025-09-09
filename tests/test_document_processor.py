import pytest
import tempfile
import shutil
import os
from unittest.mock import patch
from src.core.document_processor import DocumentProcessor

class TestDocumentProcessor:
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing"""
        # Create temp directory for vector DB
        temp_vector_dir = tempfile.mkdtemp()
        # Create temp directory for document storage 
        temp_doc_dir = tempfile.mkdtemp()
        
        yield temp_vector_dir, temp_doc_dir
        
        # Cleanup
        shutil.rmtree(temp_vector_dir, ignore_errors=True)
        shutil.rmtree(temp_doc_dir, ignore_errors=True)
    
    @pytest.fixture
    def processor(self, temp_dirs):
        """Create DocumentProcessor instance for testing"""
        temp_vector_dir, temp_doc_dir = temp_dirs
        
        # Mock the DATA_DIR to use our temp directory
        with patch('src.core.document_utils.DATA_DIR', temp_doc_dir):
            processor = DocumentProcessor(vector_db_path=temp_vector_dir)
            yield processor
    
    @pytest.fixture
    def sample_text_content(self):
        """Sample text file content for testing"""
        return "This is a sample document about machine learning. It contains information about artificial intelligence and deep learning algorithms.".encode('utf-8')
    
    def test_processor_initialization(self, processor):
        """Test that DocumentProcessor initializes correctly"""
        assert processor.vector_store is not None
        assert processor.vector_store.collection is not None
    
    def test_process_and_store_document_success(self, processor, sample_text_content):
        """Test successful document processing"""
        filename = "test_document.txt"
        
        result = processor.process_and_store_document(filename, sample_text_content)
        
        assert result["status"] == "success"
        assert result["filename"] == filename
        assert result["text_length"] > 0
        assert result["num_chunks"] > 0
        assert "file_path" in result
        assert "Successfully processed" in result["message"]
    
    def test_process_and_store_document_invalid_format(self, processor):
        """Test processing document with unsupported format"""
        filename = "test_document.xyz"  # Unsupported format
        content = b"Some content"
        
        result = processor.process_and_store_document(filename, content)
        
        assert result["status"] == "error"
        assert result["filename"] == filename
        assert "error" in result
        assert "Failed to process" in result["message"]
    
    def test_search_documents_with_results(self, processor, sample_text_content):
        """Test searching documents and finding results"""
        # First, process a document
        filename = "search_test.txt"
        processor.process_and_store_document(filename, sample_text_content)
        
        # Then search for content
        result = processor.search_documents("machine learning", n_results=3)
        
        assert result["status"] == "success"
        assert result["query"] == "machine learning"
        assert result["num_results"] > 0
        assert len(result["results"]) > 0
        
        # Check structure of results
        first_result = result["results"][0]
        assert "chunk_text" in first_result
        assert "document_name" in first_result
        assert "chunk_index" in first_result
        assert "similarity_score" in first_result
        assert "chunk_id" in first_result
        assert first_result["document_name"] == filename
    
    def test_search_documents_no_documents(self, processor):
        """Test searching when no documents are processed"""
        result = processor.search_documents("anything")
        
        # Should still work, just return empty results
        assert result["status"] == "success"
        assert result["num_results"] == 0
        assert len(result["results"]) == 0
    
    def test_list_processed_documents_empty(self, temp_dirs):
        """Test listing documents when none are processed"""
        temp_vector_dir, temp_doc_dir = temp_dirs
        
        # Create processor with isolated directories
        with patch('src.core.document_utils.DATA_DIR', temp_doc_dir):
            processor = DocumentProcessor(vector_db_path=temp_vector_dir)
            result = processor.list_processed_documents()
            
            assert result["status"] == "success"
            assert result["file_count"] == 0
            assert result["vector_chunk_count"] == 0
            assert len(result["documents"]) == 0
    
    def test_list_processed_documents_with_data(self, temp_dirs, sample_text_content):
        """Test listing documents after processing some"""
        temp_vector_dir, temp_doc_dir = temp_dirs
        
        with patch('src.core.document_utils.DATA_DIR', temp_doc_dir):
            processor = DocumentProcessor(vector_db_path=temp_vector_dir)
            
            # Process two documents
            doc1 = "document1.txt"
            doc2 = "document2.txt"
            
            processor.process_and_store_document(doc1, sample_text_content)
            processor.process_and_store_document(doc2, sample_text_content)
            
            result = processor.list_processed_documents()
            
            assert result["status"] == "success"
            assert result["file_count"] == 2
            assert result["vector_chunk_count"] > 0
            assert doc1 in result["documents"]
            assert doc2 in result["documents"]
    
    def test_get_document_chunks(self, processor, sample_text_content):
        """Test getting chunks for a specific document"""
        filename = "chunk_test.txt"
        
        # Process document first
        process_result = processor.process_and_store_document(filename, sample_text_content)
        expected_chunks = process_result["num_chunks"]
        
        # Get chunks for the document
        result = processor.get_document_chunks(filename)
        
        assert result["status"] == "success"
        assert result["document_name"] == filename
        assert result["num_chunks"] == expected_chunks
        assert len(result["chunks"]) == expected_chunks
        
        # Check chunk structure
        if result["chunks"]:
            first_chunk = result["chunks"][0]
            assert "chunk_text" in first_chunk
            assert "chunk_index" in first_chunk
            assert "chunk_length" in first_chunk
            assert "chunk_id" in first_chunk
            
        # Check chunks are sorted by index
        indices = [chunk["chunk_index"] for chunk in result["chunks"]]
        assert indices == sorted(indices)
    
    def test_get_document_chunks_nonexistent(self, processor):
        """Test getting chunks for a document that doesn't exist"""
        result = processor.get_document_chunks("nonexistent.txt")
        
        assert result["status"] == "success"  # Method doesn't fail, just returns empty
        assert result["num_chunks"] == 0
        assert len(result["chunks"]) == 0
    
    def test_multiple_documents_search(self, processor):
        """Test processing multiple documents and searching across them"""
        # Process multiple documents with different content
        doc1_content = "This document is about Python programming and software development.".encode('utf-8')
        doc2_content = "This document discusses machine learning and artificial intelligence.".encode('utf-8')
        
        processor.process_and_store_document("python_doc.txt", doc1_content)
        processor.process_and_store_document("ai_doc.txt", doc2_content)
        
        # Search for Python-related content
        python_results = processor.search_documents("Python programming", n_results=5)
        
        assert python_results["status"] == "success"
        assert python_results["num_results"] > 0
        
        # Should find content from python_doc.txt
        doc_names = [result["document_name"] for result in python_results["results"]]
        assert "python_doc.txt" in doc_names
        
        # Search for AI-related content
        ai_results = processor.search_documents("machine learning", n_results=5)
        
        assert ai_results["status"] == "success"
        assert ai_results["num_results"] > 0
        
        # Should find content from ai_doc.txt
        doc_names = [result["document_name"] for result in ai_results["results"]]
        assert "ai_doc.txt" in doc_names