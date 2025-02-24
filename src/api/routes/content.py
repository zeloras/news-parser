"""Content-related API routes."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from src.models.content import Content
from src.models.analyze import ProcessUrlRequest
from src.core.exceptions import ContentExtractionError, ContentAnalysisError
from src.services.extraction.interface import ContentExtractorInterface
from src.services.analysis.interface import ContentAnalyzerInterface
from src.services.storage.interface import ContentRepositoryInterface
from src.core.factory import get_extractor, get_analyzer, get_repository

router = APIRouter(prefix="/api/content")


@router.post("/process", response_model=Content | List[Content])
async def process_url(
    request: ProcessUrlRequest,
    extractor: ContentExtractorInterface = Depends(get_extractor),
    analyzer: ContentAnalyzerInterface = Depends(get_analyzer),
    repository: ContentRepositoryInterface = Depends(get_repository)
):
    """Process one or multiple URLs.
    
    This endpoint:
    1. Extracts content from the provided URL(s)
    2. Analyzes the content using LLM
    3. Stores the processed content in the database
    """
    try:
        request.validate_request()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    try:
        if request.url:
            # Extract content
            content = await extractor.extract_content(str(request.url))
            if not content:
                raise ContentExtractionError("Failed to extract content")
            
            # Analyze content
            content = await analyzer.analyze_content(content)
            
            # Store in database
            await repository.store(content)
            
            return content
        else:
            # Extract content
            contents = await extractor.extract_multiple([str(url) for url in request.urls])
            if not contents:
                raise ContentExtractionError("Failed to extract any content")
            
            # Analyze content
            contents = await analyzer.analyze_multiple(contents)
            
            # Store in database
            await repository.store_multiple(contents)
            
            return contents
            
    except (ContentExtractionError, ContentAnalysisError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 