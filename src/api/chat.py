from fastapi import APIRouter, Depends, UploadFile
from pydantic import BaseModel

from src.middleware.auth import get_api_key
from src.models.chat import ChatRequest, ChatResponse

from src.services.graphiti.index import query_knowledge_graph

router = APIRouter()

@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat_with_knowledge_graph(
    request: ChatRequest,
    authenticated: bool = Depends(get_api_key)
):
    """
    Chat with the knowledge graph
    
    - **query**: Chat query/question
    
    Returns AI-powered responses based on the knowledge graph
    """
    results = await query_knowledge_graph(request.query)    
    return ChatResponse(status="success", results=results)

@router.get("/health", tags=["system"])
async def health_check():
    """
    Health check endpoint
    
    Returns the status of the API
    """
    return {"status": "healthy"} 