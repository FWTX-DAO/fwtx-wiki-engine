from fastapi import APIRouter, Depends, UploadFile

from src.middleware.auth import get_api_key
from src.models.search import SearchResponse

from src.services.graphiti.index import query_knowledge_graph

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
    results = await query_knowledge_graph(query)
    return {"results": [], "query": query}

@router.get("/health", tags=["system"])
async def health_check():
    """
    Health check endpoint
    
    Returns the status of the API
    """
    return {"status": "healthy"} 