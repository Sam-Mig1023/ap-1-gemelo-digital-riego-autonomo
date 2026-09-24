"""
RAG Service for Agronomic Knowledge Retrieval
Uses LangChain + FAISS + Groq LLM
"""

from typing import List, Dict, Optional
from pathlib import Path
import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


class RAGService:
    """
    Retrieval-Augmented Generation Service
    Loads knowledge base, creates embeddings, and answers questions with sources
    """
    
    def __init__(
        self,
        knowledge_base_path: str = "backend/data/knowledge_base",
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        groq_api_key: Optional[str] = None,
        groq_model: str = "llama-3.3-70b-versatile"
    ):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.embedding_model_name = embedding_model
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.groq_model = groq_model
        
        self.embeddings = None
        self.vectorstore = None
        self.qa_chain = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Load documents, create embeddings, and initialize QA chain"""
        if self._initialized:
            return
        
        # 1. Load documents
        documents = self._load_documents()
        
        # 2. Split into chunks
        chunks = self._split_documents(documents)
        
        # 3. Create embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 4. Create FAISS vector store
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        
        # 5. Initialize LLM
        llm = ChatGroq(
            api_key=self.groq_api_key,
            model_name=self.groq_model,
            temperature=0.3,
            max_tokens=1024
        )
        
        # 6. Create custom prompt
        prompt_template = self._get_prompt_template()
        
        # 7. Create RetrievalQA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 4}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template}
        )
        
        self._initialized = True
    
    def _load_documents(self) -> List:
        """Load all markdown documents from knowledge base"""
        loader = DirectoryLoader(
            str(self.knowledge_base_path),
            glob="**/*.md",
            show_progress=True
        )
        return loader.load()
    
    def _split_documents(self, documents: List) -> List:
        """Split documents into manageable chunks with overlap"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_documents(documents)
    
    def _get_prompt_template(self) -> PromptTemplate:
        """Custom prompt template for agronomic context"""
        template = """Eres un asistente agronómico experto especializado en riego variable (VRI) y gemelos digitales.

Contexto relevante de la base de conocimiento:
{context}

Pregunta: {question}

Instrucciones:
1. Responde de forma precisa y técnica basándote SOLO en el contexto proporcionado
2. Si la información no está en el contexto, indícalo claramente
3. Cita las fuentes cuando sea posible (nombre del archivo o sección)
4. Usa términos agronómicos apropiados
5. Responde en el mismo idioma de la pregunta (español o inglés)

Respuesta:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def query(
        self,
        question: str,
        language: str = "es"
    ) -> Dict[str, any]:
        """
        Query the RAG system
        
        Args:
            question: User's question
            language: Language code (es/en)
        
        Returns:
            Dict with 'answer' and 'sources'
        """
        if not self._initialized:
            self.initialize()
        
        # Execute query
        result = self.qa_chain({"query": question})
        
        # Format response
        answer = result["result"]
        source_documents = result.get("source_documents", [])
        
        sources = [
            {
                "content": doc.page_content[:200] + "...",
                "metadata": doc.metadata
            }
            for doc in source_documents
        ]
        
        return {
            "answer": answer,
            "sources": sources,
            "model": self.groq_model,
            "num_sources": len(sources)
        }
    
    def health_check(self) -> Dict[str, any]:
        """Check if RAG service is healthy"""
        return {
            "initialized": self._initialized,
            "knowledge_base_exists": self.knowledge_base_path.exists(),
            "groq_api_key_set": bool(self.groq_api_key),
            "embedding_model": self.embedding_model_name,
            "groq_model": self.groq_model
        }


# Singleton instance
_rag_service_instance: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create RAG service singleton"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance
