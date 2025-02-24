"""Tests for content repository."""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from langchain.schema import Document
from src.services.storage.repository import ChromaRepository
from src.models.content import Content
from src.core.exceptions import DatabaseError, SearchError


@pytest_asyncio.fixture(scope="function")
async def repository():
    """Create repository instance."""
    with patch("chromadb.PersistentClient"):
        return ChromaRepository()


@pytest_asyncio.fixture(scope="function")
async def test_content():
    """Create test content."""
    return Content(
        url="https://example.com",
        title="Test Title",
        content="Test content for storage",
        source="example.com",
        summary="Test summary",
        topics=["topic1"],
        keywords=["key1"],
        sentiment="positive",
        reading_time=2,
        published_at=datetime.now(),
        language="en",
        author=""
    )


@pytest.mark.asyncio
async def test_store_content_success(repository, test_content):
    """Test successful content storage."""
    with patch.object(repository.vectorstore, "add_documents") as mock_add:
        await repository.store(test_content)
        assert mock_add.called


@pytest.mark.asyncio
async def test_store_content_failure(repository, test_content):
    """Test content storage failure."""
    with patch.object(repository.vectorstore, "add_documents", side_effect=Exception("Storage failed")):
        with pytest.raises(DatabaseError):
            await repository.store(test_content)


@pytest.mark.asyncio
async def test_store_multiple_success(repository, test_content):
    """Test storing multiple content items."""
    contents = [test_content, test_content]
    
    with patch.object(repository.vectorstore, "add_documents") as mock_add:
        await repository.store_multiple(contents)
        assert mock_add.called


@pytest.mark.asyncio
async def test_search_success(repository):
    """Test successful content search."""
    now = datetime.now()
    test_docs = [
        Document(
            page_content="Test content",
            metadata={
                "url": "https://example.com",
                "title": "Test",
                "content": "Content",
                "source": "example.com",
                "summary": "Test summary",
                "topics": "topic1, topic2",
                "keywords": "key1, key2",
                "sentiment": "positive",
                "reading_time": 2,
                "published_at": now.isoformat(),
                "language": "en",
                "author": ""
            }
        )
    ]
    
    with patch.object(repository.vectorstore, "similarity_search", return_value=test_docs):
        results = await repository.search("test query")
        assert len(results) == 1
        assert results[0].url == "https://example.com"


@pytest.mark.asyncio
async def test_search_failure(repository):
    """Test search failure."""
    with patch.object(repository.vectorstore, "similarity_search", side_effect=Exception("Search failed")):
        with pytest.raises(SearchError):
            await repository.search("test query") 