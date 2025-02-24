"""Content analysis models."""
from typing import List
from pydantic import BaseModel, Field


class ContentAnalysis(BaseModel):
    """Model for content analysis results."""
    
    summary: str = Field(
        default="",
        description="A concise summary of the content"
    )
    topics: List[str] = Field(
        default_factory=list,
        description="Main topics discussed in the content"
    )
    sentiment: str = Field(
        default="neutral",
        description="Overall sentiment of the content"
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Key terms and phrases from the content"
    )
    reading_time: int = Field(
        default=0,
        description="Estimated reading time in minutes"
    )
    author: str = Field(
        default="",
        description="Author of the content if mentioned"
    ) 