"""
Unit tests for RAG Service
Tests document loading, vectorstore creation, and query functionality
"""

import pytest
from pathlib import Path
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rag_service import RAGService, get_rag_service


# Test questions in Spanish (covers different knowledge areas)
TEST_QUESTIONS = [
    "¿Cuánta agua necesita el maíz durante la floración?",
    "¿Qué tipos de suelo son mejores para riego por aspersión?",
    "¿Cuáles son las normativas de riego en zonas áridas?",
    "¿Cuál es el mejor momento del día para regar cultivos?",
    "Según el dataset público, ¿cuántos eventos de riego hubo en la zona 1?"
]


class TestRAGService:
    """Test suite for RAG Service"""
    
    @pytest.fixture
    def rag_service(self):
        """Create RAG service instance for testing"""
        # Use environment variables or test config
        service = RAGService(
            knowledge_base_path="backend/data/knowledge_base"
        )
        return service
    
    def test_service_initialization(self, rag_service):
        """Test that RAG service initializes without errors"""
        assert rag_service is not None
        assert not rag_service._initialized
        
        # Initialize
        rag_service.initialize()
        
        assert rag_service._initialized
        assert rag_service.embeddings is not None
        assert rag_service.vectorstore is not None
        assert rag_service.qa_chain is not None
    
    def test_health_check(self, rag_service):
        """Test health check functionality"""
        health = rag_service.health_check()
        
        assert "initialized" in health
        assert "knowledge_base_exists" in health
        assert "groq_api_key_set" in health
        assert "embedding_model" in health
        assert "groq_model" in health
        
        # Knowledge base should exist
        assert health["knowledge_base_exists"] is True
    
    def test_singleton_pattern(self):
        """Test that get_rag_service returns same instance"""
        service1 = get_rag_service()
        service2 = get_rag_service()
        
        assert service1 is service2
    
    @pytest.mark.parametrize("question", TEST_QUESTIONS)
    def test_query_functionality(self, rag_service, question):
        """Test query with different agronomic questions"""
        # Initialize service
        rag_service.initialize()
        
        # Execute query
        result = rag_service.query(question=question, language="es")
        
        # Verify response structure
        assert "answer" in result
        assert "sources" in result
        assert "model" in result
        assert "num_sources" in result
        
        # Verify answer is non-empty
        assert len(result["answer"]) > 0
        
        # Verify at least one source is returned
        assert result["num_sources"] >= 1
        assert len(result["sources"]) >= 1
        
        # Verify source structure
        for source in result["sources"]:
            assert "content" in source
            assert "metadata" in source
            assert len(source["content"]) > 0
    
    def test_bilingual_support(self, rag_service):
        """Test that service handles both Spanish and English"""
        rag_service.initialize()
        
        # Spanish query
        result_es = rag_service.query(
            question="¿Qué es el riego variable?",
            language="es"
        )
        assert len(result_es["answer"]) > 0
        
        # English query
        result_en = rag_service.query(
            question="What is variable rate irrigation?",
            language="en"
        )
        assert len(result_en["answer"]) > 0
    
    def test_source_citations(self, rag_service):
        """Test that sources include proper metadata"""
        rag_service.initialize()
        
        result = rag_service.query(
            question="¿Qué tipos de sensores de humedad existen?",
            language="es"
        )
        
        # Check that sources have metadata
        for source in result["sources"]:
            metadata = source["metadata"]
            # Should have file source information
            assert "source" in metadata or "file" in metadata or len(metadata) > 0


# Manual testing script (run with: python -m pytest backend/tests/test_rag_service.py -v)
if __name__ == "__main__":
    print("\n" + "="*60)
    print("RAG SERVICE MANUAL TEST")
    print("="*60 + "\n")
    
    # Check environment
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  WARNING: GROQ_API_KEY not set in environment")
        print("   Create backend/.env file with your API key")
        print("   Example: GROQ_API_KEY=your_key_here\n")
    
    # Create service
    print("Initializing RAG service...")
    service = RAGService()
    
    # Health check
    print("\n1. Health Check:")
    health = service.health_check()
    for key, value in health.items():
        status = "✅" if value else "❌"
        print(f"   {status} {key}: {value}")
    
    # Initialize
    print("\n2. Initializing knowledge base...")
    try:
        service.initialize()
        print("   ✅ Initialization successful")
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        exit(1)
    
    # Test queries
    print("\n3. Testing queries:")
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n   Question {i}: {question}")
        try:
            import time
            start = time.time()
            result = service.query(question=question, language="es")
            elapsed = time.time() - start
            
            print(f"   ⏱️  Response time: {elapsed:.2f}s")
            print(f"   📚 Sources found: {result['num_sources']}")
            print(f"   💬 Answer preview: {result['answer'][:150]}...")
            
            if elapsed > 5.0:
                print(f"   ⚠️  WARNING: Response time exceeds 5 seconds!")
            
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
    
    print("\n" + "="*60)
    print("Manual test completed!")
    print("="*60 + "\n")
