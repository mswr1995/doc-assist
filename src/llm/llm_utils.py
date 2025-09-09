from typing import Dict, List, Optional
import ollama
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Structure for LLM responses"""
    answer: str
    sources: List[str]
    model_used: str
    success: bool
    error_message: Optional[str] = None


class OllamaClient:
    """
    Client for interacting with Ollama LLM server.
    Handles connection, prompt formatting, and response parsing.
    """

    def __init__(self, model_name: str = "llama3.2:1b", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client.
        
        Args:
            model_name: Name of the Ollama model to use
            base_url: Ollama server URL
        """
        self.model_name = model_name
        self.base_url = base_url
        self.client = ollama.Client(host=base_url)

    def test_connection(self) -> bool:
        """
        Test if Ollama server is running and model is available.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            models_response = self.client.list()
            
            if not hasattr(models_response, 'models'):
                return False
                
            models = models_response.models
            model_names = []
            
            for model in models:
                if hasattr(model, 'model'):
                    model_names.append(model.model)
            
            return self.model_name in model_names
            
        except Exception:
            return False

    def simple_test(self) -> bool:
        """
        Simple test to check if Ollama can generate responses.
        
        Returns:
            True if generation successful, False otherwise
        """
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt="Say 'Hello'",
                stream=False
            )
            return hasattr(response, 'response')
        except Exception:
            return False

    def create_rag_prompt(self, query: str, relevant_chunks: List[Dict]) -> str:
        """
        Create a structured prompt for RAG with document chunks.
        
        Args:
            query: User's question
            relevant_chunks: List of relevant document chunks with metadata
            
        Returns:
            Formatted prompt string
        """
        context_parts = []
        for i, chunk in enumerate(relevant_chunks):
            context_parts.append(
                f"[SOURCE {i+1}: {chunk['document_name']}]\n"
                f"{chunk['chunk_text']}\n"
            )
        
        context = "\n".join(context_parts)
        
        prompt = f"""You are a helpful assistant that answers questions based on provided documents.

CONTEXT FROM DOCUMENTS:
{context}

QUESTION: {query}

INSTRUCTIONS:
- Answer the question using ONLY the information provided in the context above
- If you cannot answer based on the provided context, say "I cannot find this information in the provided documents"
- Always cite your sources by mentioning the document name
- Be precise and factual
- Do not make up information not found in the context

ANSWER:"""
        
        return prompt

    def generate_answer(self, query: str, relevant_chunks: List[Dict]) -> LLMResponse:
        """
        Generate an answer based on query and relevant document chunks.
        
        Args:
            query: User's question
            relevant_chunks: List of relevant chunks from vector search
            
        Returns:
            LLMResponse with answer and source information
        """
        try:
            prompt = self.create_rag_prompt(query, relevant_chunks)
            
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                stream=False,
                options={
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 500
                }
            )
            
            if hasattr(response, 'response'):
                answer = response.response.strip()
            else:
                answer = str(response).strip()
            
            sources = list(set([chunk['document_name'] for chunk in relevant_chunks]))
            
            return LLMResponse(
                answer=answer,
                sources=sources,
                model_used=self.model_name,
                success=True
            )
            
        except Exception as e:
            return LLMResponse(
                answer="",
                sources=[],
                model_used=self.model_name,
                success=False,
                error_message=str(e)
            )

    def answer_question_with_context(self, query: str, document_chunks: List[Dict]) -> Dict:
        """
        High-level method to answer a question with document context.
        
        Args:
            query: User's question
            document_chunks: List of relevant document chunks
            
        Returns:
            Dictionary with formatted response
        """
        llm_response = self.generate_answer(query, document_chunks)
        
        return {
            "query": query,
            "answer": llm_response.answer,
            "sources": llm_response.sources,
            "model_used": llm_response.model_used,
            "success": llm_response.success,
            "error": llm_response.error_message,
            "num_sources": len(document_chunks)
        }


if __name__ == "__main__":
    client = OllamaClient()
    
    if client.test_connection() and client.simple_test():
        # Test RAG functionality with mock data
        test_chunks = [
            {
                "chunk_text": "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.",
                "document_name": "ai_overview.pdf",
                "chunk_index": 0
            }
        ]
        
        result = client.answer_question_with_context("What is machine learning?", test_chunks)
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Answer: {result['answer']}")