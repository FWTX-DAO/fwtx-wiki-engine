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
    from src.services.graphiti.index import init
    from src.config import settings
    
    logger.info("Initializing database with TOP structure...")
    
    # Determine sync mode from config
    sync_mode = settings.SYNC_MODE
    load_initial_data = settings.LOAD_INITIAL_DATA
    
    logger.info(f"Configuration:")
    logger.info(f"  - OpenAI Model: {settings.OPENAI_MODEL}")
    logger.info(f"  - Load Initial Data: {load_initial_data}")
    logger.info(f"  - Sync Mode: {sync_mode}")
    logger.info(f"  - AI Agent Enabled: {settings.SYNC_USE_AI_AGENT}")
    
    try:
        # Initialize with data loading based on configuration
        await init(
            load_initial_data_flag=load_initial_data,
            sync_mode=sync_mode
        )
        logger.info("TOP structure and data initialization complete")
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        raise


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