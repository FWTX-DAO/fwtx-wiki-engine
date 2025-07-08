from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    status: str
    results: List[dict]