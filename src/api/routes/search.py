"""Search-related API routes."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from src.models.content import Content
from src.services.storage.interface import ContentRepositoryInterface
from src.core.factory import get_repository
from src.core.exceptions import SearchError

router = APIRouter(prefix="/api/search")


@router.get("/content", response_model=List[Content])
async def search_content(
    query: str,
    limit: int = None,
    repository: ContentRepositoryInterface = Depends(get_repository)
):
    """Search content by query."""
    try:
        results = await repository.search(query, limit)
        return results
    except SearchError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}") 