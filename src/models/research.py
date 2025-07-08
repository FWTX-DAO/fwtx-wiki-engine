from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ResearchRequest(BaseModel):
    topic: str
    data_requirements: Optional[List[str]] = None
    search_queries: Optional[List[str]] = None


class ResearchResponse(BaseModel):
    topic: str
    status: str
    episodes_created: int
    results_summary: Optional[str] = None