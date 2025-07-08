"""
API endpoints for data synchronization management.
"""

from fastapi import APIRouter, Depends, HTTPException

from src.middleware.auth import get_api_key
from src.services.sync.scheduler import manual_sync, get_scheduler_status

from src.models.sync import SyncRequest, SyncResponse

router = APIRouter(prefix="/api/sync", tags=["sync"])

@router.post("/trigger", response_model=SyncResponse)
async def trigger_sync(
    request: SyncRequest,
    authenticated: bool = Depends(get_api_key)
):
    """
    Manually trigger a data synchronization.
    
    - **sync_type**: Type of sync to perform
      - full: Complete resync of all data
      - incremental: Sync only recent changes
      - services: Sync service URLs from fwtx.json
      - governance: Sync governance structure
    """
    if not authenticated:
        raise HTTPException(status_code=401, detail="Authentication required for sync operations")
    
    result = await manual_sync(request.sync_type)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Sync failed"))
    
    return SyncResponse(**result)


@router.get("/status")
async def get_sync_status(authenticated: bool = Depends(get_api_key)):
    """
    Get the status of scheduled sync jobs.
    
    Returns information about running jobs and their schedules.
    """
    return get_scheduler_status()