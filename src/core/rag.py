from typing import Dict, List, Optional
from src.core.document_processor import DocumentProcessor
from src.llm.llm_utils import OllamaClient
from src.config import config


class RAGEngine:
    """
    Retrieval-Augmented Generation engine that combines search
    with LLM generation to answer questions based on uploaded documents.

    This is the main orchestrator that connects:
    1. Document processing and search
    2. LLM-based answer generation
    """

    def __init__(
            self,
            vector_db_path: str = None,
            model_name: str = None,
            max_chunks: int = None
    ):
        """
        Initialize RAG engine with config defaults.
        """
        # use config defaults if not provided
        vector_db_path = vector_db_path or config.VECTOR_DB_PATH
        model_name = model_name or config.OLLAMA_MODEL
        max_chunks = max_chunks or config.MAX_CHUNKS
        
        # initialize our two main components
        self.document_processor = DocumentProcessor(vector_db_path = vector_db_path)
        self.llm_client = OllamaClient(model_name = model_name)
        self.max_chunks = max_chunks

        # test connections on initialization
        self._verify_connections()

    def _verify_connections(self) -> None:
        """
        Verify that both document processor and LLm are working.

        Raises:
            RuntimeError: if connection fail
        """
        if not self.llm_client.test_connection():
            raise RuntimeError("Failed to connect to Ollama LLM. Make sure Ollama is running.")
        
        # document processor should always wwork (creates DB if needed)
        doc_info = self.document_processor.list_processed_documents()
        if doc_info["status"] != "success":
            raise RuntimeError("Failed to initialize document processor.")
        
    def ask_question(self, question: str, n_chunks: Optional[int] = None) -> Dict:
        """
        Complete RAG pipeline: search document + generate answer.

        This is the main method users will call. It:
        1. Searches for relevant document chunks.
        2. Generates an answer using LLM
        3. Returns structured response with sources

        Args:
            question: User's question
            n_chunks: Number of chunks to retrieve (uses default if Mone)

        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            # step 1: Search for relevant document chunks
            n_chunks = n_chunks or self.max_chunks
            search_results = self.document_processor.search_documents(
                query = question,
                n_results = n_chunks
            )

            # check if we found any relevant chunks
            if search_results["status"] != "success":
                return {
                    "question": question,
                    "answer": "Failed to search documents.",
                    "sources": [],
                    "success": False,
                    "error": search_results.get("error", "Unknown search error"),
                    "chunks_found": 0
                }
            
            # check if we have any results
            if search_results["num_results"] == 0:
                return {
                    "question": question,
                    "answer": "I couldn't find any relevant information in the uploaded documents to answer you question.",
                    "sources": [],
                    "success": True,
                    "error": None,
                    "chunks_found": 0
                }
            
            # step 2: use LLM to generate answer from chunks
            llm_response = self.llm_client.answer_question_with_context(
                query = question,
                document_chunks = search_results["results"]
            )

            # step 3: return complete response
            return {
                "question": question,
                "answer": llm_response["answer"],
                "sources": llm_response["sources"],
                "success": llm_response["success"],
                "error": llm_response.get("error"),
                "chunks_found": search_results["num_results"],
                "model_used": llm_response["model_used"]
            }
        
        except Exception as e:
            return {
                "question": question,
                "answer": "An error occurred while processing your question.",
                "sources": [],
                "success": False,
                "error": str(e),
                "chunks_found": 0
            }
    
    def upload_and_process_document(self, filename: str, content: bytes) -> Dict:
        """
        Upload a new document and make it available for questioning.
        
        Args:
            filename: Name of the document file
            content: Raw file content as bytes
            
        Returns:
            Dictionary with processing results
        """
        return self.document_processor.process_and_store_document(filename, content)
    
    def list_available_documents(self) -> Dict:
        """
        Get list of all processed documents available for questioning.
        
        Returns:
            Dictionary with document list and statistics
        """
        return self.document_processor.list_processed_documents()
    
    def get_system_status(self) -> Dict:
        """
        Get status of all system components.
        
        Returns:
            Dictionary with health check information
        """
        try:
            # Check LLM connection
            llm_status = self.llm_client.test_connection()
            
            # Check document system
            doc_info = self.document_processor.list_processed_documents()
            doc_status = doc_info["status"] == "success"
            
            return {
                "llm_connected": llm_status,
                "document_system_ready": doc_status,
                "total_documents": doc_info.get("file_count", 0),
                "total_chunks": doc_info.get("vector_chunk_count", 0),
                "model_name": self.llm_client.model_name,
                "system_ready": llm_status and doc_status
            }
            
        except Exception as e:
            return {
                "llm_connected": False,
                "document_system_ready": False,
                "system_ready": False,
                "error": str(e)
            }

if __name__ == "__main__":
    # Demo of complete RAG system
    try:
        # Initialize RAG engine
        rag = RAGEngine()
        
        # Check system status
        status = rag.get_system_status()
        print("System Status:")
        print(f"- LLM Connected: {status['llm_connected']}")
        print(f"- Documents Available: {status.get('total_documents', 0)}")
        print(f"- System Ready: {status.get('system_ready', False)}")
        
        if status.get('system_ready'):
            # Test with sample document
            sample_doc = """
            Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed. It uses algorithms to identify patterns in data and make predictions or decisions.
            
            Deep learning is a specialized form of machine learning that uses neural networks with multiple layers to model and understand complex patterns in data.
            """.encode('utf-8')
            
            # Upload sample document
            upload_result = rag.upload_and_process_document("ml_intro.txt", sample_doc)
            if upload_result["status"] == "success":
                print(f"\nUploaded sample document with {upload_result['num_chunks']} chunks")
                
                # Ask a question
                response = rag.ask_question("What is machine learning?")
                print(f"\nQuestion: {response['question']}")
                print(f"Answer: {response['answer']}")
                print(f"Sources: {response['sources']}")
                print(f"Success: {response['success']}")
            
    except Exception as e:
        print(f"Failed to initialize RAG system: {e}")