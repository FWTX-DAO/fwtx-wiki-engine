import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from logging import INFO

from contextlib import asynccontextmanager
from dotenv import load_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.models.ontology import add_episode
from src.db.falkor import falkor_driver
from src.config import settings
from src.api.search import router

# Configure logging
logging.basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    logger.info("Starting up FWTX NextGen Wiki API")
    logger.info("--- Application Settings ---")
    logger.info(f"Allowed Origins: {settings.ALLOWED_ORIGINS if settings.ALLOWED_ORIGINS else '[Not Set - Allowing all by default in middleware]'}")
    logger.info(f"Docs Enabled: {settings.DOCS_ENABLED}")
    logger.info(f"API Key: {'Set' if settings.API_KEY else 'Not Set - Authentication Disabled'}")
    logger.info(f"OpenAI API Base: {settings.OPENAI_API_BASE}")
    logger.info(f"OpenAI API Key: {'Set' if settings.OPENAI_API_KEY else 'Not Set'}")
    logger.info(f"OpenAI Model: {settings.OPENAI_MODEL}")
    logger.info("--------------------------")

    if not settings.API_KEY:
        logger.warning("API_KEY not set in environment. Authentication is disabled.")
    
    yield
    
    # Shutdown event
    logger.info("Shutting down FWTX Wiki API")

# Create FastAPI app
app = FastAPI(
    title="FWTX Wiki API",
    description="API for FWTX Wiki",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DOCS_ENABLED else None,
    redoc_url="/redoc" if settings.DOCS_ENABLED else None,
    openapi_url="/openapi.json" if settings.DOCS_ENABLED else None,
)

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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()] if settings.ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("wiki:app", host="0.0.0.0", port=8001, reload=True)

