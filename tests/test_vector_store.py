import pytest
import tempfile
import shutil
import os
from src.core.vector_store import VectorStore

class TestVectorStore:
    
    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory for ChromaDB during tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup after test
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def vector_store(self, temp_db_dir):
        """Create a VectorStore instance with temporary directory"""
        return VectorStore(persist_directory=temp_db_dir)
    
    def test_init_vector_store(self, vector_store):
        """Test VectorStore initialization"""
        assert vector_store.client is not None
        assert vector_store.collection is None
    
    def test_get_or_create_collection(self, vector_store):
        """Test creating/getting a collection"""
        collection = vector_store.get_or_create_collection("test_collection")
        
        assert collection is not None
        assert vector_store.collection is not None
        assert vector_store.collection.name == "test_collection"
    
    def test_add_document_chunks(self, vector_store):
        """Test adding document chunks to vector store"""
        # Setup
        vector_store.get_or_create_collection()
        chunks = [
            "This is the first chunk about dogs.",
            "This is the second chunk about cats.",
            "This is the third chunk about birds."
        ]
        document_name = "test_animals.txt"
        
        # Add chunks
        vector_store.add_document_chunks(chunks, document_name)
        
        # Verify chunks were added
        info = vector_store.get_collection_info()
        assert info["count"] == 3
    
    def test_add_chunks_with_metadata(self, vector_store):
        """Test adding chunks with custom metadata"""
        vector_store.get_or_create_collection()
        chunks = ["Test chunk with metadata"]
        document_name = "test_doc.txt"
        metadata = [{"page": 1, "section": "intro"}]
        
        vector_store.add_document_chunks(chunks, document_name, metadata)
        
        # Verify it was added
        info = vector_store.get_collection_info()
        assert info["count"] == 1
    
    def test_search_similar_chunks(self, vector_store):
        """Test searching for similar chunks"""
        # Setup - add some test chunks
        vector_store.get_or_create_collection()
        chunks = [
            "Dogs are loyal pets and great companions.",
            "Cats are independent animals that like to sleep.",
            "Python is a programming language used for AI."
        ]
        vector_store.add_document_chunks(chunks, "test_search.txt")
        
        # Search for something related to dogs
        results = vector_store.search_similar_chunks("pets and animals", n_results=2)
        
        # Verify results structure
        assert "chunks" in results
        assert "metadata" in results
        assert "distances" in results
        assert "ids" in results
        
        # Should return 2 results
        assert len(results["chunks"]) == 2
        assert len(results["metadata"]) == 2
    
    def test_search_without_collection(self, vector_store):
        """Test searching when no collection is initialized"""
        with pytest.raises(ValueError, match="No collection initialized"):
            vector_store.search_similar_chunks("test query")
    
    def test_get_collection_info_empty(self, vector_store):
        """Test getting info when no collection exists"""
        info = vector_store.get_collection_info()
        assert "error" in info
        assert info["error"] == "No collection initialized"
    
    def test_get_collection_info_with_data(self, vector_store):
        """Test getting collection info with data"""
        vector_store.get_or_create_collection("info_test")
        chunks = ["Test chunk 1", "Test chunk 2"]
        vector_store.add_document_chunks(chunks, "info_test.txt")
        
        info = vector_store.get_collection_info()
        
        assert info["name"] == "info_test"
        assert info["count"] == 2
        assert "metadata" in info
    
    def test_multiple_documents(self, vector_store):
        """Test adding chunks from multiple documents"""
        vector_store.get_or_create_collection()
        
        # Add chunks from first document
        chunks1 = ["First doc chunk 1", "First doc chunk 2"]
        vector_store.add_document_chunks(chunks1, "doc1.txt")
        
        # Add chunks from second document
        chunks2 = ["Second doc chunk 1"]
        vector_store.add_document_chunks(chunks2, "doc2.txt")
        
        # Verify total count
        info = vector_store.get_collection_info()
        assert info["count"] == 3
        
        # Search and verify we can get results from both documents
        results = vector_store.search_similar_chunks("chunk", n_results=3)
        
        # Debug: Print the actual metadata structure
        print("Actual metadata:", results["metadata"])
        print("First metadata keys:", results["metadata"][0].keys() if results["metadata"] else "No metadata")
        
        # Check that we have chunks from both documents
        doc_names = [meta["document_name"] for meta in results["metadata"]]
        assert "doc1.txt" in doc_names
        assert "doc2.txt" in doc_names