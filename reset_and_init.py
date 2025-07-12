#!/usr/bin/env python3
"""
Reset the FalkorDB database and initialize with TOP structure.

This script:
1. Clears the existing database
2. Builds new indices and constraints
3. Loads initial TOP-compliant data
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def reset_database():
    """Reset the FalkorDB database."""
    from src.db.falkor import falkor_driver
    
    logger.info("Resetting FalkorDB database...")
    
    try:
        # Clear all nodes and relationships
        await falkor_driver.run("MATCH (n) DETACH DELETE n")
        logger.info("Cleared all nodes and relationships")
        
        # Clear all indices
        await falkor_driver.run("CALL db.idx.fulltext.drop('entity')")
        await falkor_driver.run("CALL db.idx.fulltext.drop('episode')")
        logger.info("Dropped existing indices")
        
    except Exception as e:
        logger.warning(f"Error during reset (may be normal if indices don't exist): {e}")
    
    await falkor_driver.close()
    logger.info("Database reset complete")


async def initialize_with_top():
    """Initialize the database with TOP structure."""
    from src.services.graphiti.index import graphiti, init
    from src.services.sync.data_loader import DataLoader
    
    logger.info("Initializing database with TOP structure...")
    
    try:
        # Initialize Graphiti with new indices
        await graphiti.build_indices_and_constraints()
        logger.info("Built new indices and constraints")
        
        # Add initial TOP ontology episode
        from src.models.ontology import add_episode as add_ontology_episode
        await add_ontology_episode(graphiti, episode_type="general")
        logger.info("Added TOP ontology episode")
        
        # Load data from all sources using DataLoader
        logger.info("Loading Fort Worth data from local files and AI research...")
        loader = DataLoader(graphiti)
        await loader.sync_to_graphiti()
        logger.info("All data loaded successfully")
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        raise
    finally:
        await graphiti.close()
        logger.info("Initialization complete")


async def main():
    """Main function to reset and initialize."""
    logger.info("Starting database reset and initialization...")
    
    # Step 1: Reset the database
    await reset_database()
    
    # Step 2: Initialize with TOP structure
    await initialize_with_top()
    
    logger.info("Reset and initialization complete!")
    logger.info("You can now start the application with: uv run wiki.py")


if __name__ == "__main__":
    asyncio.run(main())