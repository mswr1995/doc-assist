from typing import Dict, List, Optional
import os
from pathlib import Path

# import our existing modules
from src.core.document_utils import save_document, read_documents, list_documents
from src.core.text_processor import extract_text_from_bytes, chunk_text, clean_text
from src.core.vector_store import VectorStore


class DocumentProcessor:
    """
    High-level document processing pipeline that coordinates:
    1. Document storage (file system)
    2. Text extraction and processing
    3. Vector storage (searchable embeddings)
    """

    def __init__(self, vector_db_path: str = "./chroma_db"):
        """
        Initialize the document procesor.

        Args:
            vector_db_path: path where chromadb will store vector data
        """
        # Initialize our vector store
        self.vector_store = VectorStore(persist_directory = vector_db_path)
        self.vector_store.get_or_create_collection("documents")

        print(f"DocumentProcessor initialized with vector store at: {vector_db_path}")

    def process_and_store_document(self, filename: str, content: bytes) -> Dict:
        """
        Complete pipeline: save file -> extract text -> chunk -> store in vector DB

        Args:
            filename: name of the document file
            content: RAW file content as byte

        Returns:
            Dictionary with processing results and metadata
        """
        try:
            # step 1: save the file to disk
            file_path = save_document(filename, content)
            print(f"Saved document: {filename}")

            # step 2: extract text based on file extension
            file_extension = Path(filename).suffix.lower()
            raw_text = extract_text_from_bytes(content, file_extension)
            print(f"Extracted {len(raw_text)} characters from {filename}")

            # step 3: clean the extracted text
            cleaned_text = clean_text(raw_text)
            print(f"Cleaned text: {len(cleaned_text)} characters")

            # step 4: split text into chunks
            chunks = chunk_text(cleaned_text, chunk_size = 1000, overlap = 200)
            print(f" Created {len(chunks)} chunks from document")

            # step 5: store the chunks in vector database
            self.vector_store.add_document_chunks(
                chunks = chunks,
                document_name = filename,
                chunk_metadata = None # we could add page numbers, etc. here
            )
            print(f"Stored {len(chunks)} chunks in vector database")

            # return summary of what was processed
            return {
                "status": "success",
                "filename": filename,
                "file_path": file_path,
                "text_length": len(cleaned_text),
                "num_chunks": len(chunks),
                "message": f"Successfully processed {filename}"
            }
        
        except Exception as e:
            # if anything goes wrong, return error details
            return {
                "status": "error",
                "filename": filename,
                "error": str(e),
                "message": f"Failed to process {filename}: {str(e)}"
            }
        
    def search_documents(self, query: str, n_results: int = 5) -> Dict:
        """
        Search for document chunks relevant to a query.
        
        Args:
            query: The question or search text
            n_results: maximum number of relevant chunks to return
        
            Returns:
                Dictionary with search and metadata
        """
        try:
            # use our vector store to find similar chunks
            results = self.vector_store.search_similar_chunks(query, n_results)

            # format the results for easier use
            formatted_results = []
            for i, chunk in enumerate(results["chunks"]):
                chunk_info = {
                    "chunk_text": chunk,
                    "document_name": results["metadata"][i]["document_name"],
                    "chunk_index": results["metadata"][i]["chunk_index"],
                    "similarity_score": 1 - results["distances"][i], # convert distance to similarity
                    "chunk_id": results["ids"][i]
                }
                formatted_results.append(chunk_info)

            return {
                "status": "success",
                "query": query,
                "num_results": len(formatted_results),
                "results": formatted_results,
                "message": f"Found {len(formatted_results)} relevant chunks"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "query": query,
                "error": str(e),
                "message": f"Search failed: {str(e)}"
            }
        
    def list_processed_documents(self) -> Dict:
        """
        Get a list of processed documents.

        Returns:
            Dictionary with document list and stats
        """
        try:
            # get documents from file system
            file_documents = list_documents()

            # get info fromvector store
            vector_info = self.vector_store.get_collection_info()

            return {
                "status": "success",
                "file_count": len(file_documents),
                "vector_chunk_count": vector_info.get("count", 0),
                "documents": file_documents,
                "message": f"Found {len(file_documents)} processed documents"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": f"Failed to list documents: {str(e)}"
            }
        
    def get_document_chunks(self, document_name: str) -> Dict:
        """Get all chunks for a specific document
        
        Args:
            document_name: name of the document to get chunks for

        Returns:
            Dictionary with document chunks
        """
        try:
            # search for all chunks from this document
            # we use the document name as query and get many results
            results = self.vector_store.search_similar_chunks(
                query = document_name,
                n_results = 100 # get up to 100 chunks
            )

            # filter to only chunks from the requested document
            document_chunks = []
            for i, chunk in enumerate(results["chunks"]):
                if results["metadata"][i]["document_name"] == document_name:
                    chunk_info = {
                        "chunk_text": chunk,
                        "chunk_index": results["metadata"][i]["chunk_index"],
                        "chunk_length": results["metadata"][i]["chunk_length"],
                        "chunk_id": results["ids"][i]
                    }
                    document_chunks.append(chunk_info)

            # sort by chunk index to maintain order
            document_chunks.sort(key = lambda x: x["chunk_index"])

            return {
                "status": "success",
                "document_name": document_name,
                "num_chunks": len(document_chunks),
                "chunks": document_chunks,
                "message": f"Found {len(document_chunks)} chunks for {document_name}"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "document_name": document_name,
                "error": str(e),
                "message": f"Failed to get chunks for {document_name}: {str(e)}"
            }