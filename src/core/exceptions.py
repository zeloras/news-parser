class ContentProcessingException(Exception):
    """Base exception for all content processing errors."""
    pass


class ContentExtractionError(ContentProcessingException):
    """Raised when content extraction fails."""
    pass


class ContentAnalysisError(ContentProcessingException):
    """Raised when content analysis fails."""
    pass


class SearchError(ContentProcessingException):
    """Raised when search operations fail."""
    pass


class DatabaseError(ContentProcessingException):
    """Raised when database operations fail."""
    pass 