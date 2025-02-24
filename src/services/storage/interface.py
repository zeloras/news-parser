"""Content storage interface."""
from abc import ABC, abstractmethod
from typing import List

from src.models.content import Content


class ContentRepositoryInterface(ABC):
    """Interface for content storage."""
    
    @abstractmethod
    async def store(self, content: Content) -> None:
        """Store content in database.
        
        Args:
            content: Content to store.
            
        Raises:
            DatabaseError: If storage fails.
        """
        pass
    
    @abstractmethod
    async def store_multiple(self, contents: List[Content]) -> None:
        """Store multiple content items in database.
        
        Args:
            contents: List of content items to store.
            
        Raises:
            DatabaseError: If storage fails.
        """
        pass
    
    @abstractmethod
    async def search(self, query: str, limit: int = None) -> List[Content]:
        """Search content in database.
        
        Args:
            query: Search query.
            limit: Maximum number of results to return.
            
        Returns:
            List[Content]: List of matching content items.
            
        Raises:
            SearchError: If search fails.
        """
        pass 