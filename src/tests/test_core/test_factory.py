"""Tests for factory functions."""
import pytest
from src.core.factory import get_extractor, get_analyzer, get_repository
from src.services.extraction.extractor import PlaywrightExtractor
from src.services.analysis.analyzer import OpenAIAnalyzer
from src.services.storage.repository import ChromaRepository


def test_get_extractor():
    """Test get_extractor returns correct instance."""
    extractor = get_extractor()
    assert isinstance(extractor, PlaywrightExtractor)


def test_get_analyzer():
    """Test get_analyzer returns correct instance."""
    analyzer = get_analyzer()
    assert isinstance(analyzer, OpenAIAnalyzer)


def test_get_repository():
    """Test get_repository returns correct instance."""
    repository = get_repository()
    assert isinstance(repository, ChromaRepository) 