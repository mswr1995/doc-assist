import pytest
import os
import tempfile
from src.core.document_utils import save_document, read_documents, list_documents, ensure_data_dir

class TestDocumentUtils:
    
    def test_ensure_data_dir(self):
        """Test that data directory is created"""
        ensure_data_dir()
        from src.core.document_utils import DATA_DIR
        assert os.path.exists(DATA_DIR)
    
    def test_save_document(self):
        """Test saving a document"""
        content = b"This is test content"
        filename = "test_file.txt"
        
        file_path = save_document(filename, content)
        
        assert os.path.exists(file_path)
        assert filename in file_path
    
    def test_read_documents(self):
        """Test reading a document"""
        # First save a document
        content = b"Hello World"
        filename = "read_test.txt"
        save_document(filename, content)
        
        # Then read it
        read_content = read_documents(filename)
        assert read_content == content
    
    def test_read_nonexistent_document(self):
        """Test reading a file that doesn't exist"""
        with pytest.raises(FileNotFoundError):
            read_documents("nonexistent_file.txt")
    
    def test_list_documents(self):
        """Test listing documents"""
        # Save a couple of test files
        save_document("list_test1.txt", b"content1")
        save_document("list_test2.txt", b"content2")
        
        documents = list_documents()
        
        assert "list_test1.txt" in documents
        assert "list_test2.txt" in documents
        assert len(documents) >= 2