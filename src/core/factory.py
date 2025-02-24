"""Service factory module."""
from src.services.extraction.interface import ContentExtractorInterface
from src.services.analysis.interface import ContentAnalyzerInterface
from src.services.storage.interface import ContentRepositoryInterface
from src.services.extraction.extractor import PlaywrightExtractor
from src.services.analysis.analyzer import OpenAIAnalyzer
from src.services.storage.repository import ChromaRepository
from src.core.config import get_settings

settings = get_settings()


def get_extractor() -> ContentExtractorInterface:
    """Get content extractor instance."""
    return PlaywrightExtractor()


def get_analyzer() -> ContentAnalyzerInterface:
    """Get content analyzer instance."""
    return OpenAIAnalyzer()


def get_repository() -> ContentRepositoryInterface:
    """Get content repository instance."""
    return ChromaRepository() 