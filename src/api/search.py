from fastapi import APIRouter, Depends, UploadFile

from app.core.security import get_api_key
from models.search import SearchResponse
from services.markdown_service import convert_file_to_text

router = APIRouter()

@router.post("/search", response_model=ConversionResponse, tags=["search"])
async def search_knowledge_graph(
    authenticated: bool = Depends(get_api_key)
):
    """
    Convert a file to markdown
    
    - **file**: File to convert
    
    Returns the converted markdown
    """
    text = await convert_file_to_text(file)
    return {"result": text}

@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check():
    """
    Health check endpoint
    
    Returns the status of the API
    """
    return {"status": "healthy"} 