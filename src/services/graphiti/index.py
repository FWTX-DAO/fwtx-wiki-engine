import logging
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF
from graphiti_core.utils.bulk_utils import RawEpisode
from graphiti_core.llm_client.openai_client import OpenAIClient
from graphiti_core.embedder import OpenAIEmbedder
from src.db.falkor import falkor_driver
from src.models.ontology import add_episode as add_ontology_episode, entity_types, edge_types, edge_type_map
from src.services.sync.fort_worth_data import initialize_live_research
from src.services.graphiti.initial_sync import load_initial_data
from src.services.graphiti.search_config import TOPSearchConfig, TOPSearchQueries, top_search
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
        # Initialize the graph database with graphiti's indices. This only needs to be done once.
        await graphiti.build_indices_and_constraints()
        logger.info("Graph indices and constraints built successfully")
        
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
    use_custom_filter: bool = False
):
    """
    Query the knowledge graph with optional TOP-specific filters.
    
    Args:
        query: Search query
        entity_category: Filter by category ('government', 'political', 'legal', 'geographic')
        use_custom_filter: Whether to use TOP custom filters
    """
    logger.info(f"Searching for: {query}")
    
    if use_custom_filter:
        results = await top_search(
            graphiti,
            query,
            entity_category=entity_category
        )
    else:
        results = await graphiti.search(
            query,
            entity_types=entity_types,
            edge_types=edge_types
        )

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


# Export search helpers
__all__ = [
    'graphiti',
    'init',
    'query_knowledge_graph',
    'TOPSearchConfig',
    'TOPSearchQueries',
    'top_search'
]