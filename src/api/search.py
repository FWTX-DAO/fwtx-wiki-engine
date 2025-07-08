from fastapi import APIRouter, Depends, UploadFile

from src.middleware.auth import get_api_key
from src.models.search import SearchResponse

router = APIRouter()

@router.post("/search", response_model=SearchResponse, tags=["search"])
async def search_knowledge_graph(
    query: str,
    authenticated: bool = Depends(get_api_key)
):
    """
    Search the knowledge graph
    
    - **query**: Search query
    
    Returns search results from the knowledge graph
    """
    # TODO: Implement knowledge graph search
    return {"results": [], "query": query}

@router.get("/health", tags=["system"])
async def health_check():
    """
    Health check endpoint
    
    Returns the status of the API
    """
    return {"status": "healthy"} 