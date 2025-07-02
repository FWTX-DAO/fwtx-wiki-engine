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

from graphiti_core.driver.falkordb_driver import FalkorDriver
from episodes import add_episodes

# FalkorDB connection using FalkorDriver
falkor_driver = FalkorDriver(
    host='localhost',        # or os.environ.get('FALKORDB_HOST', 'localhost')
    port='6379',            # or os.environ.get('FALKORDB_PORT', '6379')
    username=None,          # or os.environ.get('FALKORDB_USERNAME', None)
    password=None           # or os.environ.get('FALKORDB_PASSWORD', None)
)

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
# Neo4j connection parameters
# Make sure Neo4j Desktop is running with a local DBMS started
neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
neo4j_password = os.environ.get('NEO4J_PASSWORD', 'password')

if not neo4j_uri or not neo4j_user or not neo4j_password:
    raise ValueError('NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set')

async def init():

    try:
        # Initialize the graph database with graphiti's indices. This only needs to be done once.
        await graphiti.build_indices_and_constraints()
        await add_episodes(graphiti)
        # Additional code will go here
        
    finally:
        # Close the connection
        await graphiti.close()
        print('\nConnection closed')

async def main():
    # Main function implementation will go here
    # Perform a hybrid search combining semantic similarity and BM25 retrieval
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

