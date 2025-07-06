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

    # OpenAI API Settings (optional)
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings() 