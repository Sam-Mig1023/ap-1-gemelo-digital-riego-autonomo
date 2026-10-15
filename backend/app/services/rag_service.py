"""
RAG Service for Agronomic Knowledge Retrieval
Uses LangChain + FAISS + Groq LLM
"""

from typing import List, Dict, Optional
from pathlib import Path
import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document


class RAGService:
    """
    Retrieval-Augmented Generation Service
    Loads knowledge base, creates embeddings, and answers questions with sources
    """
    
    def __init__(
        self,
        knowledge_base_path: Optional[str] = None,
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        groq_api_key: Optional[str] = None,
        groq_model: Optional[str] = None
    ):
        backend_root = Path(__file__).resolve().parents[2]
        configured_path = knowledge_base_path or os.getenv("KNOWLEDGE_BASE_PATH")
        if configured_path:
            requested_path = Path(configured_path).expanduser()
            if requested_path.is_absolute():
                self.knowledge_base_path = requested_path.resolve()
            else:
                candidates = (
                    Path.cwd() / requested_path,
                    backend_root / requested_path,
                    backend_root.parent / requested_path,
                )
                self.knowledge_base_path = next(
                    (candidate.resolve() for candidate in candidates if candidate.is_dir()),
                    (backend_root / requested_path).resolve(),
                )
        else:
            self.knowledge_base_path = backend_root / "data" / "knowledge_base"
        self.embedding_model_name = embedding_model
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.groq_model = groq_model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        
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
        if not documents:
            raise RuntimeError(
                f"No Markdown documents found in the RAG knowledge base: {self.knowledge_base_path}"
            )

        if not self.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured. Add a valid Groq API key to backend/.env to enable RAG chat."
            )
        
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
        documents = []
        kb_path = self.knowledge_base_path

        if not kb_path.is_dir():
            raise FileNotFoundError(f"RAG knowledge base directory does not exist: {kb_path}")
        
        # Cargar todos los archivos .md
        for md_file in kb_path.glob("**/*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Crear documento con metadata
                    doc = Document(
                        page_content=content,
                        metadata={"source": str(md_file)}
                    )
                    documents.append(doc)
                    print(f"[OK] Loaded: {md_file.name}")
            except Exception as e:
                print(f"[WARN] Error loading {md_file.name}: {e}")
        
        print(f"\n[INFO] Total documents loaded: {len(documents)}")
        return documents
    
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
