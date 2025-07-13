"""
Initial synchronization module for Fort Worth data.

This module provides data loading functionality for the knowledge graph,
aligned with the Texas Ontology Protocol (TOP) strategy using AI agents.
"""

import logging

logger = logging.getLogger(__name__)


async def load_initial_data(graphiti):
    """
    Load initial Fort Worth data into Graphiti.
    
    This function loads structured data from local files and optionally
    fetches additional data using AI research agents.
    """
    from src.services.sync.data_loader import DataLoader
    from src.services.sync.top_loader import load_top_compliant_data
    
    # First load TOP-compliant base data
    logger.info("Loading TOP-compliant Fort Worth data...")
    await load_top_compliant_data(graphiti)
    
    # Then load additional data from files
    logger.info("Loading data from local files...")
    data_loader = DataLoader(graphiti)
    await data_loader.sync_to_graphiti()
    
    logger.info("Initial data loading completed")