"""
Data models for chat API endpoints.
"""

from pydantic import BaseModel
from typing import List, Optional, Any


class ChatRequest(BaseModel):
    """Request model for chat operations."""
    query: str
    message: Optional[str] = None  # Alias for query
    entity_category: Optional[str] = None  # Filter by TOP category
    use_custom_filter: Optional[bool] = False
    
    @property
    def effective_query(self) -> str:
        """Return the effective query (message takes precedence)."""
        return self.message or self.query


class ChatResponse(BaseModel):
    """Response model for chat operations."""
    status: str
    results: List[Any]
    response: Optional[str] = None
    metadata: Optional[dict] = None