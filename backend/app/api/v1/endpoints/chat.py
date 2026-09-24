"""
Chat endpoint for RAG-powered agronomic assistant
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

from app.services.rag_service import get_rag_service


router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model"""
    question: str = Field(..., min_length=1, max_length=1000)
    language: str = Field(default="es", pattern="^(es|en)$")


class SourceDocument(BaseModel):
    """Source document reference"""
    content: str
    metadata: Dict


class ChatResponse(BaseModel):
    """Chat response model"""
    answer: str
    sources: List[SourceDocument]
    model: str
    num_sources: int


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest):
    """
    RAG-powered chat endpoint
    
    Returns answer with cited sources from knowledge base
    """
    try:
        rag_service = get_rag_service()
        result = rag_service.query(
            question=request.question,
            language=request.language
        )
        return ChatResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG query failed: {str(e)}"
        )


@router.get("/chat/health", status_code=status.HTTP_200_OK)
async def chat_health():
    """Health check for RAG service"""
    try:
        rag_service = get_rag_service()
        health = rag_service.health_check()
        
        if not health["initialized"]:
            # Try to initialize
            rag_service.initialize()
            health = rag_service.health_check()
        
        return health
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"RAG service unhealthy: {str(e)}"
        )
