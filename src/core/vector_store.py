import chromadb
from typing import List, Dict, Optional
import uuid


class VectorStore:
    """
    Manages Chromadb vector store for document embeddings and search.
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize chromadb client.

        Args:
            persist_directory: where to store the database files
        """
        # Create a persistent client(saves to disk)
        self.client = chromadb.PersistentClient(path = persist_directory)
        self.collection = None

    def get_or_create_collection(self, collection_name: str = "documents"):
        """
        Get existing collection or create a new one.

        Args:
            collection_name: name of the collection

        Returns:
            Chromadb collection object
        """
        self.collection = self.client.get_or_create_collection(
            name = collection_name,
            metadata = {"description": "Document chunks for RAG"}
        )
        return self.collection
    
    def add_document_chunks(self, chunks: List[str], document_name: str, chunk_metadata: Optional[List[Dict]] = None):
        """
        Add document chunks to the vector store.

        Args:
            chunks: List of text chunks to add
            document_name: name of the source document
            chunk_metadata: optional metadata for each chunk
        """
        if not self.collection:
            self.get_or_create_collection()

        # Generate unique IDs for each chunk
        ids = [f"{document_name}_chunk_{i}_{uuid.uuid4().hex[:8]}" for i in range(len(chunks))]

        # create metadata for each chunk
        metadatas = []
        for i, chunk in enumerate(chunks):
            metadata = {
                "document_name": document_name,  # ✅ Change 'chunk_name' to 'document_name'
                "chunk_index": i,
                "chunk_length": len(chunk)
            }
            # Add any additional metadata if provided
            if chunk_metadata and i < len(chunk_metadata):
                metadata.update(chunk_metadata[i])
            metadatas.append(metadata)

        # Add chunks to Chromadb (it automatically creates embeddings)
        self.collection.add(
            documents = chunks,
            metadatas = metadatas,
            ids = ids
        )

        print(f"Added {len(chunks)} chunks from document '{document_name}' to vector store")

    def search_similar_chunks(self, query: str, n_results: int = 5) -> Dict:
        """
        Search for chunks similar to the query.

        Args:
            query: The search text
            n_results: Number of similar chunks to return

        Returns:
            Dictionary with similar chunks and their metadata
        """
        if not self.collection:
            raise ValueError("No collection initialized. Call get_or_create_collection() first.")
        
        # Query Chromadb for similar chunks
        results = self.collection.query(
            query_texts = [query],
            n_results = n_results
        )

        return {
            "chunks": results["documents"][0],
            "metadata": results["metadatas"][0],
            "distances": results["distances"][0],
            "ids": results["ids"][0]
        }
        
    def get_collection_info(self) -> Dict:
        """
        Get information about the current collection.

        Returns:
            Dictionary with collection statistics
        """
        if not self.collection:
            return {"error": "No collection initialized"}

        count = self.collection.count()
        return {
            "name": self.collection.name,
            "count": count,
            "metadata": self.collection.metadata
        }