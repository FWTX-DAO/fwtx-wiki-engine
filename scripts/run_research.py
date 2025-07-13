#!/usr/bin/env python3
"""
Manually run the AI research agent to populate Fort Worth data.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Reduce noise from HTTP requests
logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv()


async def run_live_research():
    """Run live research using AI agents."""
    from src.services.graphiti.index import graphiti
    from src.services.sync.fort_worth_data import initialize_live_research
    
    logger.info("=== Running Fort Worth Live Research ===")
    
    try:
        # Initialize graph indices if needed
        logger.info("Ensuring graph indices...")
        await graphiti.build_indices_and_constraints()
        
        # Run live research
        logger.info("Starting live research with AI agents...")
        fetch_tasks = await initialize_live_research(graphiti)
        
        logger.info(f"\n✓ Research completed for {len(fetch_tasks)} tasks")
        
        # Test a search to verify data
        logger.info("\nTesting knowledge graph...")
        results = await graphiti.search("Fort Worth mayor")
        logger.info(f"Search for 'Fort Worth mayor' returned {len(results)} results")
        
        if results:
            for i, result in enumerate(results[:3]):
                logger.info(f"  {i+1}. {result.fact}")
        
    except Exception as e:
        logger.error(f"Research failed: {e}", exc_info=True)
    finally:
        await graphiti.close()
        logger.info("Graph connection closed")


async def main():
    """Main entry point."""
    # Temporarily override settings to ensure research runs
    os.environ["LOAD_INITIAL_DATA"] = "true"
    os.environ["SYNC_MODE"] = "live"
    
    await run_live_research()


if __name__ == "__main__":
    asyncio.run(main())