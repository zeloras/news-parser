"""Content extraction interface."""
from abc import ABC, abstractmethod
from typing import List

from src.models.content import Content


class ContentExtractorInterface(ABC):
    """Interface for content extraction."""
    
    @abstractmethod
    async def extract_content(self, url: str) -> Content:
        """Extract content from URL.
        
        Args:
            url: URL to extract content from.
            
        Returns:
            Content: Extracted content.
            
        Raises:
            ContentExtractionError: If extraction fails.
        """
        pass
    
    @abstractmethod
    async def extract_multiple(self, urls: List[str]) -> List[Content]:
        """Extract content from multiple URLs.
        
        Args:
            urls: List of URLs to extract content from.
            
        Returns:
            List[Content]: List of extracted content items.
        """
        pass 