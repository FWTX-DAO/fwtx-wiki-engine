from fastapi import APIRouter, Depends

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
    - **entity_category**: Optional filter by category ('government', 'political', 'legal', 'geographic')
    - **use_custom_filter**: Whether to apply TOP-specific filters
    
    Returns AI-powered responses based on the knowledge graph
    """
    # Use effective query (message or query)
    query = request.effective_query
    
    # Query with optional filters
    results = await query_knowledge_graph(
        query,
        entity_category=request.entity_category,
        use_custom_filter=request.use_custom_filter
    )
    
    # Format response
    response_text = None
    if results:
        response_text = f"Found {len(results)} results for: {query}"
    else:
        response_text = f"No results found for: {query}"
    
    return ChatResponse(
        status="success",
        results=results,
        response=response_text,
        metadata={
            "total_results": len(results),
            "entity_category": request.entity_category,
            "filtered": request.use_custom_filter
        }
    )

@router.get("/health", tags=["system"])
async def health_check():
    """
    Health check endpoint
    
    Returns the status of the API
    """
    return {"status": "healthy"} 