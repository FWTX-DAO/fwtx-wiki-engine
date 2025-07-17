import logging
from graphiti_core import Graphiti
from src.db.falkor import falkor_driver
from src.models.ontology import add_episode as add_ontology_episode
from src.services.sync.fort_worth_data import initialize_live_research
from src.services.graphiti.initial_sync import load_initial_data
from src.services.graphiti.search_config import top_search
from src.config import settings

logger = logging.getLogger(__name__)

# Validate API key configuration
if not settings.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY must be set for Graphiti")

# Initialize Graphiti with OpenAI clients (default)
graphiti = Graphiti(
    graph_driver=falkor_driver,
)

logger.info(f"Graphiti initialized with OpenAI model: {settings.OPENAI_MODEL}")

async def init(load_initial_data_flag: bool = False, sync_mode: str = "initial"):
    """
    Initialize Graphiti and optionally load initial Fort Worth data.
    
    Args:
        load_initial_data_flag: Whether to load initial Fort Worth data
        sync_mode: Type of sync - 'initial' for structured data or 'live' for AI research
    """
    try:
        # Skip building indices for FalkorDB to avoid SHOW INDEXES error
        # FalkorDB will create indices automatically as needed
        logger.info("Skipping manual index creation for FalkorDB compatibility")
        
        # Add initial ontology episode with entity types
        await add_ontology_episode(graphiti, episode_type="general")
        logger.info("Ontology episode added")
        
        # Load initial data if requested
        if load_initial_data_flag:
            if sync_mode == "initial":
                logger.info("Loading initial Fort Worth structured data...")
                await load_initial_data(graphiti)
                logger.info("Initial data loaded successfully")
            elif sync_mode == "live":
                logger.info("Initializing live research for Fort Worth data...")
                await initialize_live_research(graphiti)
                logger.info("Live research initialized")
            
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        raise
    finally:
        # Close the connection
        await graphiti.close()
        logger.info('Connection closed')

async def query_knowledge_graph(
    query: str,
    entity_category: str = None,
    use_custom_filter: bool = False,
    focal_node_uuid: str = None,
    limit: int = None
):
    """
    Query the knowledge graph with hybrid search and optional contextual reranking.
    
    Args:
        query: Search query
        entity_category: Filter by category ('government', 'political', 'legal', 'geographic')
        use_custom_filter: Whether to use TOP custom filters
        focal_node_uuid: UUID of focal node for contextual reranking
        limit: Maximum number of results to return
    """
    logger.info(f"Searching for: {query}")
    
    # Use limit from settings if not provided
    if limit is None:
        limit = settings.SEARCH_RESULT_LIMIT
    
    try:
        if use_custom_filter:
            results = await top_search(
                graphiti,
                query,
                entity_category=entity_category
            )
        elif focal_node_uuid:
            # Use node distance reranking for contextual search
            logger.info(f"Using focal node reranking with node: {focal_node_uuid}")
            results = await graphiti.search(
                query,
                focal_node_uuid=focal_node_uuid
            )
        else:
            # Use standard hybrid search (semantic + BM25 with RRF)
            results = await graphiti.search(query)
        
        # Apply limit manually if specified
        if limit and len(results) > limit:
            results = results[:limit]

        # Log search results
        logger.info(f'Found {len(results)} results')
        for result in results:
            logger.debug(f'UUID: {result.uuid}')
            logger.debug(f'Fact: {result.fact}')
            if hasattr(result, 'valid_at') and result.valid_at:
                logger.debug(f'Valid from: {result.valid_at}')
            if hasattr(result, 'invalid_at') and result.invalid_at:
                logger.debug(f'Valid until: {result.invalid_at}')
        
        return results
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []


async def contextual_search(
    query: str,
    context_entities: list = None,
    limit: int = None
):
    """
    Perform contextual search for chat applications.
    
    Args:
        query: User's search query
        context_entities: List of entity UUIDs from conversation context
        limit: Maximum results to return
    """
    if limit is None:
        limit = settings.SEARCH_RESULT_LIMIT
    
    # If we have context entities, use the most relevant one as focal point
    if context_entities and len(context_entities) > 0:
        focal_node = context_entities[0]  # Use most recent/relevant entity
        logger.info(f"Using contextual search with focal entity: {focal_node}")
        return await query_knowledge_graph(
            query=query,
            focal_node_uuid=focal_node,
            limit=limit
        )
    
    # Otherwise use standard hybrid search
    return await query_knowledge_graph(query=query, limit=limit)


async def multi_turn_search(
    current_query: str,
    previous_results: list = None,
    conversation_context: dict = None,
    limit: int = None
):
    """
    Enhanced search for multi-turn conversations.
    
    Args:
        current_query: Current user query
        previous_results: Results from previous queries for context
        conversation_context: Context from previous conversation turns
        limit: Maximum results to return
    """
    if limit is None:
        limit = settings.SEARCH_RESULT_LIMIT
    
    # Extract focal nodes from previous results if available
    focal_nodes = []
    if previous_results:
        focal_nodes = [result.uuid for result in previous_results[:3]]  # Top 3
    
    # If we have conversation context, try to find relevant entities
    if conversation_context and 'entities' in conversation_context:
        focal_nodes.extend(conversation_context['entities'][:2])  # Add top 2 context entities
    
    # Use the most relevant focal node for search
    if focal_nodes:
        return await query_knowledge_graph(
            query=current_query,
            focal_node_uuid=focal_nodes[0],
            limit=limit
        )
    
    # Fallback to standard search
    return await query_knowledge_graph(query=current_query, limit=limit)


# Export search helpers
__all__ = [
    'graphiti',
    'init',
    'query_knowledge_graph',
    'contextual_search',
    'multi_turn_search',
    'TOPSearchConfig',
    'TOPSearchQueries',
    'top_search'
]