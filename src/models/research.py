"""
Data models for research API endpoints.
"""

from pydantic import BaseModel
from typing import List, Optional


class ResearchRequest(BaseModel):
    """Request model for research operations."""
    topic: str
    data_requirements: Optional[List[str]] = None
    search_queries: Optional[List[str]] = None


class ResearchResponse(BaseModel):
    """Response model for research operations."""
    topic: str
    status: str
    episodes_created: int
    results_summary: Optional[str] = None