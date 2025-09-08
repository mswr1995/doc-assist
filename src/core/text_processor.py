from typing import List
import io
try:
    from pypdf import PdfReader  # Changed from PyPDF2
    from docx import Document
except ImportError:
    PdfReader = None  # Changed from PyPDF2
    Document = None


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: The text to chunk
        chunk_size: maximum characters per chunk
        overlap: characters to overlap between chunks

    Returns:
        List of text chunks 
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap # move start position with overlap

    return chunks

def extract_text_from_bytes(content: bytes, file_extension: str) -> str:
    """
    extract text content from file bytes based on extension.
    currently supports .txt, .pdf and .docx, can be extended.

    Args:
        content: file content as bytes
        file_extension: file extension('pdf', 'txt')

    Return:
        extracted text content
    """
    file_extension = file_extension.lower()

    if file_extension == '.txt':
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback to other encodings
            try:
                return content.decode('latin-1')
            except UnicodeDecodeError:
                return content.decode('utf-8', errors = 'ignore')
            
    elif file_extension == '.pdf':
        if PdfReader is None:  # Changed from PyPDF2
            raise ImportError("pypdf is required for PDF support. Install with: uv add pypdf")
        
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PdfReader(pdf_file)  # Changed from PyPDF2.PdfReader
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
        
    elif file_extension == '.docx':
        if Document is None:
            raise ImportError("python-docx is required for DOCX support. Install it using uv add python-docx")
        
        try:
            docx_file = io.BytesIO(content)
            doc = Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise ValueError(f"FAiled to extract text from DOCX: {str(e)}")

    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def clean_text(text: str) -> str:
    """
    clean and normalize text content

    Args:
        text: raw text content

    Return:
        cleaned text
    """
   
    # Split by lines first to preserve line breaks
    lines = text.split('\n')

    # Clean each line individually (remove excessive whitespace)
    cleaned_lines = []
    for line in lines:
        cleaned_line = ' '.join(line.split())  # Remove extra spaces within line
        if cleaned_line:  # Only add non-empty lines
            cleaned_lines.append(cleaned_line)

    return '\n'.join(cleaned_lines)