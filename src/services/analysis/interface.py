"""Content analysis interface."""
from abc import ABC, abstractmethod
from typing import List

from src.models.content import Content


class ContentAnalyzerInterface(ABC):
    """Interface for content analysis."""
    
    @abstractmethod
    async def analyze_content(self, content: Content) -> Content:
        """Analyze content using LLM.
        
        Args:
            content: Content to analyze.
            
        Returns:
            Content: Analyzed content with summary, topics, etc.
            
        Raises:
            ContentAnalysisError: If analysis fails.
        """
        pass
    
    @abstractmethod
    async def analyze_multiple(self, contents: List[Content]) -> List[Content]:
        """Analyze multiple content items.
        
        Args:
            contents: List of content items to analyze.
            
        Returns:
            List[Content]: List of analyzed content items.
        """
        pass 