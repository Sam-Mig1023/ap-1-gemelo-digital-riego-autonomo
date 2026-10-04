"""
Langflow Integration Router
This endpoint connects the VRI Digital Twin with a Langflow instance.
It forwards agronomic chat queries to the Langflow API.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import httpx
import os

router = APIRouter()

# Langflow default local URL
LANGFLOW_API_URL = os.getenv("LANGFLOW_API_URL", "http://127.0.0.1:7860/api/v1/run")
# If you export a specific flow from Langflow, you define its ID here
LANGFLOW_FLOW_ID = os.getenv("LANGFLOW_FLOW_ID", "agronomic-rag-flow-id")

class LangflowRequest(BaseModel):
    message: str
    language: str = "es"
    
@router.post("/chat-langflow")
async def chat_with_langflow(request: LangflowRequest):
    """
    Forwards the user question to the Langflow backend.
    Langflow is responsible for executing the RAG logic visually constructed in its UI.
    """
    try:
        # Langflow expects an input dictionary matching the Chat Input node
        payload = {
            "input_value": request.message,
            "output_type": "chat",
            "input_type": "chat",
            "tweaks": {
                "Language": request.language
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LANGFLOW_API_URL}/{LANGFLOW_FLOW_ID}",
                json=payload,
                timeout=60.0
            )
            
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Langflow API error")
            
        # Parse Langflow response structure
        data = response.json()
        message = data.get("outputs", [])[0].get("outputs", [])[0].get("results", {}).get("message", {}).get("text", "")
        
        return {
            "answer": message,
            "sources": [], # Langflow handles citations in text
            "model": "Langflow-Visual-Agent"
        }
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Cannot connect to Langflow: {str(e)}")
