"""Content models for the application."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator, Field


class Content(BaseModel):
    """Model for content data."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "url": "https://example.com/news",
                "title": "Sample Title",
                "content": "Content...",
                "source": "News Source",
                "author": "Author Name",
                "published_at": "2025-02-23T14:30:00",
                "language": "en",
                "keywords": ["news", "technology"],
                "topics": ["technology trends"],
                "summary": "Brief summary",
                "sentiment": "positive",
                "reading_time": 5
            }
        }
    )
    
    url: str
    title: str
    content: str
    source: str
    published_at: datetime = Field(default_factory=datetime.now)
    language: str = "en"
    author: str = ""
    summary: str = ""
    topics: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    sentiment: str = "neutral"
    reading_time: int = 0
    
    @field_validator('content')
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        """Validate that content is not empty."""
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()
    
    def to_metadata(self) -> dict:
        """Convert content to ChromaDB compatible metadata.
        
        Returns a dict with all metadata as simple types (str, int, float, bool)
        that ChromaDB can store.
        """
        published_at_str = self.published_at.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "url": str(self.url),
            "title": str(self.title),
            "source": str(self.source),
            "author": str(self.author),
            "published_at": published_at_str,
            "language": str(self.language),
            "summary": str(self.summary),
            "sentiment": str(self.sentiment),
            "reading_time": int(self.reading_time),
            "keywords": ",".join(str(k) for k in self.keywords),
            "topics": ",".join(str(t) for t in self.topics)
        }


class SearchQuery(BaseModel):
    """Model for enhanced search query with semantic expansion."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True
    )
    
    expanded_terms: List[str] = Field(
        description="List of semantically related search terms (3-5 terms)",
        min_length=1,
        max_length=5
    )
    main_topics: List[str] = Field(
        description="Main topics or themes from the query (1-3 topics)",
        min_length=1,
        max_length=3
    )

    @classmethod
    def from_query(cls, query: str) -> "SearchQuery":
        clean_query = query.replace('#', '').strip()
        return cls(expanded_terms=[clean_query], main_topics=[clean_query]) 