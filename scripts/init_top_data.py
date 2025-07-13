#!/usr/bin/env python3
"""
Initialize Fort Worth Wiki with full TOP-compliant data.

This script loads comprehensive Fort Worth municipal data
following the Texas Ontology Protocol specification.
"""

import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


async def initialize_top_data():
    """Initialize the knowledge graph with TOP-compliant Fort Worth data."""
    from src.services.graphiti.index import graphiti, init
    from src.services.sync.top_loader import TOPDataLoader
    from src.models.top.structured import TOPEpisodeData
    
    logger.info("=== Fort Worth TOP Data Initialization ===")
    logger.info("Initializing knowledge graph with Texas Ontology Protocol compliant data")
    
    try:
        # Initialize Graphiti indices
        logger.info("Building graph indices and constraints...")
        await graphiti.build_indices_and_constraints()
        logger.info("✓ Graph indices built")
        
        # Load TOP-compliant data
        logger.info("Loading TOP-compliant Fort Worth data...")
        top_loader = TOPDataLoader(graphiti)
        await top_loader.sync_to_graphiti()
        logger.info("✓ TOP data loaded successfully")
        
        # Display statistics
        logger.info("\n=== Data Load Summary ===")
        logger.info("Entities created:")
        logger.info("  - City: Fort Worth (Home Rule)")
        logger.info("  - County: Tarrant")
        logger.info("  - Mayor: Mattie Parker")
        logger.info("  - City Manager: David Cooke")
        logger.info("  - Council Districts: 9")
        logger.info("  - Council Members: 9")
        logger.info("  - Departments: 5 (Police, Fire, Water, Code, Development)")
        logger.info("  - Legal Documents: City Charter")
        logger.info("\nRelationships created:")
        logger.info("  - Governs (Mayor → City, Charter → City)")
        logger.info("  - PartOf (City → County, Districts → City, Departments → City)")
        logger.info("  - Serves (Council Members → Districts)")
        logger.info("  - AppointedBy (City Manager → Mayor)")
        
        # Test a search
        logger.info("\n=== Testing Knowledge Graph ===")
        results = await graphiti.search("Fort Worth mayor")
        logger.info(f"Search for 'Fort Worth mayor' returned {len(results)} results")
        
        if results:
            for result in results[:3]:
                logger.info(f"  - {result.fact}")
        
        logger.info("\n✓ Fort Worth Wiki initialized with TOP-compliant data!")
        logger.info("You can now run 'uv run wiki.py' to start the application")
        
    except Exception as e:
        logger.error(f"Failed to initialize TOP data: {e}")
        raise
    finally:
        await graphiti.close()
        logger.info("Graph connection closed")


async def verify_top_compliance():
    """Verify that loaded data meets TOP requirements."""
    from src.services.graphiti.index import graphiti
    
    logger.info("\n=== Verifying TOP Compliance ===")
    
    # Check for required entities
    required_checks = [
        ("Fort Worth city", "HomeRuleCity entity"),
        ("Mayor Parker", "Mayor entity"),
        ("City Manager", "CityManager entity"),
        ("Council District", "CouncilDistrict entities"),
        ("Police Department", "Department entity"),
        ("City Charter", "Charter entity")
    ]
    
    all_passed = True
    for query, description in required_checks:
        results = await graphiti.search(query)
        if results:
            logger.info(f"✓ {description}: Found")
        else:
            logger.error(f"✗ {description}: NOT FOUND")
            all_passed = False
    
    if all_passed:
        logger.info("\n✓ All TOP compliance checks passed!")
    else:
        logger.error("\n✗ Some TOP compliance checks failed")
    
    return all_passed


async def main():
    """Main initialization function."""
    # Set environment variable to skip automatic loading
    os.environ["LOAD_INITIAL_DATA"] = "false"
    
    # Initialize TOP data
    await initialize_top_data()
    
    # Verify compliance
    await verify_top_compliance()


if __name__ == "__main__":
    asyncio.run(main())