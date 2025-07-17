from fastapi import APIRouter, Depends

from src.middleware.auth import get_api_key
from src.models.chat import ChatRequest, ChatResponse

from src.services.graphiti.index import query_knowledge_graph, contextual_search

router = APIRouter()

@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat_with_knowledge_graph(
    request: ChatRequest,
    authenticated: bool = Depends(get_api_key)
):
    """
    Chat with the knowledge graph using advanced search capabilities
    
    - **query**: Chat query/question
    - **entity_category**: Optional filter by category ('government', 'political', 'legal', 'geographic')
    - **use_custom_filter**: Whether to apply TOP-specific filters
    - **context_entities**: List of entity UUIDs for contextual search
    - **use_contextual_search**: Enable contextual search with focal node reranking
    - **limit**: Maximum number of results to return
    
    Returns AI-powered responses based on the knowledge graph
    """
    # Use effective query (message or query)
    query = request.effective_query
    
    # Choose search method based on request parameters
    if request.use_contextual_search and request.context_entities:
        # Use contextual search with focal node reranking
        results = await contextual_search(
            query=query,
            context_entities=request.context_entities,
            limit=request.limit
        )
    else:
        # Use standard search with optional filters
        results = await query_knowledge_graph(
            query,
            entity_category=request.entity_category,
            use_custom_filter=request.use_custom_filter,
            limit=request.limit
        )
    
    # Format response with actual information
    response_text = None
    if results:
        # Extract the most relevant facts from the results
        facts = []
        seen_facts = set()  # Track unique facts to avoid duplicates
        
        # Sort results by validity date (most recent first) if available
        sorted_results = sorted(results, key=lambda x: (
            getattr(x, 'valid_at', None) or 
            getattr(x, 'created_at', None) or 
            '1900-01-01'
        ), reverse=True)
        
        for result in sorted_results:
            if hasattr(result, 'fact') and result.fact:
                fact = result.fact.strip()
                if fact not in seen_facts:
                    facts.append(fact)
                    seen_facts.add(fact)
        
        if facts:
            # Join the unique facts into a coherent response
            response_text = "\n\n".join(facts[:3])  # Limit to top 3 unique facts
        else:
            response_text = f"I found information about \"{query}\" in the Fort Worth knowledge graph."
    else:
        response_text = f"I don't have information about \"{query}\" in the Fort Worth knowledge graph. You might want to try a different search or check if the data has been loaded."
    
    return ChatResponse(
        status="success",
        results=results,
        response=response_text,
        metadata={
            "total_results": len(results),
            "entity_category": request.entity_category,
            "filtered": request.use_custom_filter,
            "contextual_search": request.use_contextual_search,
            "context_entities": request.context_entities,
            "conversation_id": request.conversation_id,
            "search_limit": request.limit,
            "search_method": "contextual" if request.use_contextual_search and request.context_entities else "standard"
        }
    )

@router.get("/health", tags=["system"])
async def health_check():
    """
    Health check endpoint
    
    Returns the status of the API
    """
    return {"status": "healthy"} 