"""Content analysis models."""
from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from typing import List

# Request models
class ProcessUrlRequest(BaseModel):
    """Request model for content processing."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "url": "https://example.com/content",
                # or
                "urls": ["https://example.com/content1", "https://example.com/content2"]
            }
        }
    )
    
    url: HttpUrl | None = None
    urls: List[HttpUrl] | None = None
        
    def validate_request(self):
        """Validate that either url or urls is provided, but not both."""
        if bool(self.url) == bool(self.urls):
            raise ValueError("Exactly one of 'url' or 'urls' must be provided")
        return self

class ContentAnalysis(BaseModel):
    """Model for content analysis results."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True
    )
    
    title: str = Field(
        default="",
        description="Title of the content"
    )
    summary: str = Field(
        default="",
        description="A concise summary (2-3 sentences)"
    )
    topics: List[str] = Field(
        default_factory=list,
        min_length=0,
        description="Main topics discussed (3-5 topics)"
    )
    sentiment: str = Field(
        default="neutral",
        description="Overall sentiment (positive/negative/neutral)"
    )
    keywords: List[str] = Field(
        default_factory=list,
        min_length=0,
        description="Key terms and phrases (3-5 terms)"
    )
    reading_time: int = Field(
        default=0,
        description="Estimated reading time in minutes"
    )
    author: str = Field(
        default="",
        description="Content author if available"
    )

