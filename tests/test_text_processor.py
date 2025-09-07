import pytest
from src.core.text_processor import chunk_text, extract_text_from_bytes, clean_text

class TestTextProcessor:
    
    def test_chunk_text_small_text(self):
        """Test chunking text smaller than chunk_size"""
        text = "Small text"
        chunks = chunk_text(text, chunk_size=100)
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_chunk_text_large_text(self):
        """Test chunking large text with overlap"""
        text = "A" * 1000 + "B" * 1000  # 2000 characters
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        
        assert len(chunks) > 1
        # Check overlap exists
        assert chunks[1].startswith(chunks[0][-100:])
    
    def test_extract_text_from_txt(self):
        """Test extracting text from .txt file"""
        content = "Hello World".encode('utf-8')
        result = extract_text_from_bytes(content, '.txt')
        
        assert result == "Hello World"
    
    def test_extract_text_unsupported_format(self):
        """Test extracting text from unsupported format"""
        content = b"some content"
        
        with pytest.raises(ValueError, match="Unsupported file type"):
            extract_text_from_bytes(content, '.xyz')
    
    def test_clean_text(self):
        """Test text cleaning functionality"""
        dirty_text = "  Hello   World  \n\n\n  Test  \n  "
        cleaned = clean_text(dirty_text)
        
        assert cleaned == "Hello World\nTest"
        assert "  " not in cleaned  # No double spaces