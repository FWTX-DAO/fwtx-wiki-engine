import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "")
    
    # API Documentation
    DOCS_ENABLED: bool = os.getenv("DOCS_ENABLED", "true").lower() in ("1", "true", "yes")
    
    # API Authentication
    API_KEY: str = os.getenv("API_KEY", "")

    # FalkorDB Settings
    FALKORDB_HOST: str = os.getenv("FALKORDB_HOST", "localhost")
    FALKORDB_PORT: str = os.getenv("FALKORDB_PORT", "6379")
    FALKORDB_USERNAME: str | None = os.getenv("FALKORDB_USERNAME")
    FALKORDB_PASSWORD: str | None = os.getenv("FALKORDB_PASSWORD")

    # PostgreSQL Settings
    PG_USER: str = os.getenv("PG_USER", "")
    PG_PASSWORD: str = os.getenv("PG_PASSWORD", "")
    PG_URL: str = os.getenv("PG_URL", "")

    # OpenAI API Settings (optional)
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Anthropic Settings (optional)
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
    
    # Data Synchronization Settings
    ENABLE_SYNC_SCHEDULER: bool = os.getenv("ENABLE_SYNC_SCHEDULER", "false").lower() in ("1", "true", "yes")
    SYNC_INTERVAL_HOURS: int = int(os.getenv("SYNC_INTERVAL_HOURS", "24"))
    SYNC_ON_STARTUP: bool = os.getenv("SYNC_ON_STARTUP", "true").lower() in ("1", "true", "yes")
    
    # Agent Configuration
    AGENT_CACHE_ENABLED: bool = os.getenv("AGENT_CACHE_ENABLED", "true").lower() in ("1", "true", "yes")
    AGENT_CACHE_TTL_HOURS: int = int(os.getenv("AGENT_CACHE_TTL_HOURS", "24"))
    AGENT_MAX_RETRIES: int = int(os.getenv("AGENT_MAX_RETRIES", "3"))
    AGENT_TIMEOUT_SECONDS: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "300"))
    
    # Enhanced Sync Settings
    SYNC_USE_AI_AGENT: bool = os.getenv("SYNC_USE_AI_AGENT", "true").lower() in ("1", "true", "yes")
    SYNC_PDF_EXTRACTION: bool = os.getenv("SYNC_PDF_EXTRACTION", "true").lower() in ("1", "true", "yes")
    SYNC_RESEARCH_BATCH_SIZE: int = int(os.getenv("SYNC_RESEARCH_BATCH_SIZE", "5"))
    LOAD_INITIAL_DATA: bool = os.getenv("LOAD_INITIAL_DATA", "false").lower() in ("1", "true", "yes")
    SYNC_MODE: str = os.getenv("SYNC_MODE", "initial")
    
    # Search Configuration
    SEARCH_RESULT_LIMIT: int = int(os.getenv("SEARCH_RESULT_LIMIT", "10"))
    SEARCH_INCLUDE_RELATIONSHIPS: bool = os.getenv("SEARCH_INCLUDE_RELATIONSHIPS", "true").lower() in ("1", "true", "yes")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings() 