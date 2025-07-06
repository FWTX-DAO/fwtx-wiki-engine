from pydantic import BaseModel


class SearchResponse(BaseModel):
    status: str