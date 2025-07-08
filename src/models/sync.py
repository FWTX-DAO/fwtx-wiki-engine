from pydantic import BaseModel
from typing import Literal

class SyncRequest(BaseModel):
    sync_type: Literal["full", "incremental", "services", "governance"] = "incremental"


class SyncResponse(BaseModel):
    status: str
    sync_type: str
    timestamp: str
    error: str = None