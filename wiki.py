import asyncio
import logging
from logging import INFO

from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config import settings
from src.api.chat import router
from src.api.sync import router as sync_router
from src.api.research import router as research_router
from src.api.graph import router as graph_router
from src.services.graphiti.index import init as graphiti_init
from src.services.sync.scheduler import start_sync_scheduler, stop_sync_scheduler
from src.ascii_art import FULL_BANNER

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
    # Display ASCII art banner
    print(FULL_BANNER)
    
    logger.info("Starting up FWTX NextGen Wiki API")
    
    # Create compact configuration display
    config_display = f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                    APPLICATION CONFIGURATION                                      ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════╣
║ API            │ Origins: {(settings.ALLOWED_ORIGINS[:30] + '...') if settings.ALLOWED_ORIGINS and len(settings.ALLOWED_ORIGINS) > 30 else (settings.ALLOWED_ORIGINS or 'All'): <33} │ Docs: {str(settings.DOCS_ENABLED): <5} │ Auth: {'ON' if settings.API_KEY else 'OFF': <3}  ║
╠════════════════╪═══════════════════════════════════════════════════════════════════════════════════╣
║ FalkorDB       │ {settings.FALKORDB_HOST}:{settings.FALKORDB_PORT: <38} │ User: {'✓' if settings.FALKORDB_USERNAME else '✗': <5} │ Pass: {'✓' if settings.FALKORDB_PASSWORD else '✗': <3}  ║
║ PostgreSQL     │ {'Connected' if settings.PG_URL else 'Not configured': <45} │ User: {'✓' if settings.PG_USER else '✗': <5} │ Pass: {'✓' if settings.PG_PASSWORD else '✗': <3}  ║
╠════════════════╪═══════════════════════════════════════════════════════════════════════════════════╣
║ LLM Provider   │ OpenAI: {settings.OPENAI_MODEL: <23} {'[Key ✓]' if settings.OPENAI_API_KEY else '[Key ✗]': <13} │ Anthropic: {'✓' if settings.ANTHROPIC_API_KEY else '✗': <8} ║
║                │ Base URL: {settings.OPENAI_API_BASE: <60}    ║
╠════════════════╪═══════════════════════════════════════════════════════════════════════════════════╣
║ Sync Engine    │ Scheduler: {'ON' if settings.ENABLE_SYNC_SCHEDULER else 'OFF': <3} │ Interval: {settings.SYNC_INTERVAL_HOURS:>2}h │ Startup: {'Y' if settings.SYNC_ON_STARTUP else 'N': <1} │ Mode: {settings.SYNC_MODE: <8} │ AI: {'ON' if settings.SYNC_USE_AI_AGENT else 'OFF': <3} ║
║                │ Initial Data: {'Y' if settings.LOAD_INITIAL_DATA else 'N': <1} │ PDF Extract: {'Y' if settings.SYNC_PDF_EXTRACTION else 'N': <1} │ Batch Size: {settings.SYNC_RESEARCH_BATCH_SIZE: <30}   ║
╠════════════════╪═══════════════════════════════════════════════════════════════════════════════════╣
║ Agent Config   │ Cache: {'ON' if settings.AGENT_CACHE_ENABLED else 'OFF': <3} ({settings.AGENT_CACHE_TTL_HOURS:>2}h) │ Retries: {settings.AGENT_MAX_RETRIES} │ Timeout: {settings.AGENT_TIMEOUT_SECONDS}s │ Search Limit: {settings.SEARCH_RESULT_LIMIT: <13} ║
╠════════════════╪═══════════════════════════════════════════════════════════════════════════════════╣
║ Logging        │ Level: {settings.LOG_LEVEL: <10} │ Format: {settings.LOG_FORMAT: <53}    ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
    
    # Print the configuration display line by line to ensure proper formatting
    for line in config_display.strip().split('\n'):
        logger.info(line)

    if not settings.API_KEY:
        logger.warning("API_KEY not set in environment. Authentication is disabled.")
    
    # Initialize Graphiti knowledge graph
    try:
        logger.info("Initializing Graphiti knowledge graph...")
        
        # Run initialization in a background task to not block startup
        asyncio.create_task(initialize_graphiti(settings.LOAD_INITIAL_DATA, settings.SYNC_MODE))
        if settings.LOAD_INITIAL_DATA:
            logger.info(f"Graphiti initialization started in background (mode: {settings.SYNC_MODE})")
        else:
            logger.info("Graphiti initialization started (basic setup only - set LOAD_INITIAL_DATA=true to load data)")
    except Exception as e:
        logger.error(f"Failed to start Graphiti initialization: {e}")
    
    # Start sync scheduler if enabled
    if settings.ENABLE_SYNC_SCHEDULER:
        try:
            logger.info("Starting data sync scheduler...")
            start_sync_scheduler()
            logger.info("Data sync scheduler started")
        except Exception as e:
            logger.error(f"Failed to start sync scheduler: {e}")
    
    yield
    
    # Shutdown event
    logger.info("Shutting down FWTX Wiki API")
    
    # Stop sync scheduler
    try:
        stop_sync_scheduler()
    except Exception as e:
        logger.error(f"Error stopping sync scheduler: {e}")


async def initialize_graphiti(load_initial_data: bool, sync_mode: str = "initial"):
    """Background task to initialize Graphiti."""
    try:
        await graphiti_init(load_initial_data_flag=load_initial_data, sync_mode=sync_mode)
        logger.info("Graphiti initialization completed successfully")
        
        # If initial data was loaded, log some statistics
        if load_initial_data:
            logger.info(f"Initial data loaded using {sync_mode} mode")
    except Exception as e:
        logger.error(f"Graphiti initialization failed: {e}")
        # Continue running even if initialization fails
        # The app can still serve static files and handle basic requests

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
app.include_router(sync_router)
app.include_router(research_router)
app.include_router(graph_router)

# Mount static files
app.mount("/", StaticFiles(directory="client", html=True), name="static")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("wiki:app", host="0.0.0.0", port=8001, reload=True)

