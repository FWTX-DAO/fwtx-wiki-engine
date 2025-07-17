from pydantic import BaseModel
from typing import Dict, Any, List

class GraphQueryRequest(BaseModel):
    query: str
    params: Dict[str, Any] = {}


class GraphQueryResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    raw_results: List[Dict[str, Any]]