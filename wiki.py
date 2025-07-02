import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from logging import INFO

from dotenv import load_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF

from src.models.ontology import add_episode
from db.falkor import falkor_driver

# Configure logging
logging.basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

load_dotenv()
# Initialize Graphiti with Neo4j connection
graphiti = Graphiti(graph_driver=falkor_driver)

async def init():

    try:
        # Initialize the graph database with graphiti's indices. This only needs to be done once.
        await graphiti.build_indices_and_constraints()
        await add_episode(graphiti)
    finally:
        # Close the connection
        await graphiti.close()
        print('\nConnection closed')

async def main():
    # Main function implementation will go here
    # Perform a hybrid search combining semantic similarity and BM25 retrieval
    # await init() if running for the first time
    print("\nSearching for: 'Who is the City Manager of Fort Worth?'")
    results = await graphiti.search('Who is the City Manager of Fort Worth?')

    # Print search results
    print('\nSearch Results:')
    for result in results:
        print(f'UUID: {result.uuid}')
        print(f'Fact: {result.fact}')
        if hasattr(result, 'valid_at') and result.valid_at:
            print(f'Valid from: {result.valid_at}')
        if hasattr(result, 'invalid_at') and result.invalid_at:
            print(f'Valid until: {result.invalid_at}')
        print('---')


if __name__ == '__main__':
    asyncio.run(main())

