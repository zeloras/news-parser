"""Tests for API routes."""
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import datetime
from fastapi import HTTPException

from src.main import app
from src.models.content import Content
from src.core.exceptions import ContentExtractionError, ContentAnalysisError, SearchError
from src.core.factory import get_extractor, get_analyzer, get_repository


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest_asyncio.fixture(scope="function")
async def mock_services():
    """Mock all services."""
    mock_extractor = AsyncMock()
    mock_analyzer = AsyncMock()
    mock_repo = AsyncMock()
    
    # Override FastAPI dependency injection
    app.dependency_overrides[get_extractor] = lambda: mock_extractor
    app.dependency_overrides[get_analyzer] = lambda: mock_analyzer
    app.dependency_overrides[get_repository] = lambda: mock_repo
    
    yield {
        "extractor": mock_extractor,
        "analyzer": mock_analyzer,
        "repository": mock_repo
    }
    
    # Clear dependency overrides after test
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_process_single_url_success(client, mock_services):
    """Test successful processing of single URL."""
    now = datetime.now()
    test_content = Content(
        url="https://example.com",
        title="Test",
        content="Content",
        source="example.com",
        published_at=now,
        language="en",
        author="",
        summary="Test summary",
        topics=["topic1"],
        keywords=["key1"],
        sentiment="positive",
        reading_time=2
    )
    
    mock_services["extractor"].extract_content.return_value = test_content
    mock_services["analyzer"].analyze_content.return_value = test_content
    mock_services["repository"].store.return_value = None
    
    response = client.post(
        "/api/content/process",
        json={"url": "https://example.com"}
    )
    
    assert response.status_code == 200
    assert response.json()["url"].rstrip("/") == test_content.url.rstrip("/")


@pytest.mark.asyncio
async def test_process_multiple_urls_success(client, mock_services):
    """Test successful processing of multiple URLs."""
    now = datetime.now()
    test_content = Content(
        url="https://example.com",
        title="Test",
        content="Content",
        source="example.com",
        published_at=now,
        language="en",
        author="",
        summary="Test summary",
        topics=["topic1"],
        keywords=["key1"],
        sentiment="positive",
        reading_time=2
    )
    
    mock_services["extractor"].extract_multiple.return_value = [test_content]
    mock_services["analyzer"].analyze_multiple.return_value = [test_content]
    mock_services["repository"].store_multiple.return_value = None
    
    response = client.post(
        "/api/content/process",
        json={"urls": ["https://example.com"]}
    )
    
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_search_content_success(client, mock_services):
    """Test successful content search."""
    now = datetime.now()
    test_content = Content(
        url="https://example.com",
        title="Test",
        content="Content",
        source="example.com",
        published_at=now,
        language="en",
        author="",
        summary="Test summary",
        topics=["topic1"],
        keywords=["key1"],
        sentiment="positive",
        reading_time=2
    )
    
    # Configure mock to return exactly one result
    mock_services["repository"].search.return_value = [test_content]
    
    response = client.get("/api/search/content?query=test")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["url"] == test_content.url


@pytest.mark.asyncio
async def test_search_content_with_limit(client, mock_services):
    """Test content search with limit parameter."""
    now = datetime.now()
    test_contents = [
        Content(
            url=f"https://example{i}.com",
            title=f"Test {i}",
            content=f"Content {i}",
            source="example.com",
            published_at=now,
            language="en",
            author="",
            summary=f"Test summary {i}",
            topics=["topic1"],
            keywords=["key1"],
            sentiment="positive",
            reading_time=2
        ) for i in range(3)
    ]
    
    # Configure mock to return exactly two results when limit=2
    mock_services["repository"].search.return_value = test_contents[:2]
    
    response = client.get("/api/search/content?query=test&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["url"] == test_contents[0].url
    assert data[1]["url"] == test_contents[1].url


@pytest.mark.asyncio
async def test_search_content_empty_results(client, mock_services):
    """Test content search with no results."""
    # Configure mock to return empty list
    mock_services["repository"].search.return_value = []
    
    response = client.get("/api/search/content?query=nonexistent")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.asyncio
async def test_search_content_search_error(client, mock_services):
    """Test content search with search error."""
    # Configure mock to raise SearchError
    mock_services["repository"].search.side_effect = SearchError("Search failed")
    
    response = client.get("/api/search/content?query=test")
    
    assert response.status_code == 500
    error = response.json()
    assert "Search failed" in error["detail"]


@pytest.mark.asyncio
async def test_search_content_general_error(client, mock_services):
    """Test content search with unexpected error."""
    # Configure mock to raise unexpected error
    mock_services["repository"].search.side_effect = Exception("Unexpected error")
    
    response = client.get("/api/search/content?query=test")
    
    assert response.status_code == 500
    error = response.json()
    assert "Search failed: Unexpected error" in error["detail"]


@pytest.mark.asyncio
async def test_process_single_url_extraction_error(client, mock_services):
    """Test content extraction error handling."""
    # Configure mock to raise ContentExtractionError
    mock_services["extractor"].extract_content.side_effect = ContentExtractionError("Failed to extract content")
    
    response = client.post(
        "/api/content/process",
        json={"url": "https://example.com"}
    )
    
    assert response.status_code == 422
    assert "Failed to extract content" in response.json()["detail"]


@pytest.mark.asyncio
async def test_process_single_url_analysis_error(client, mock_services):
    """Test content analysis error handling."""
    now = datetime.now()
    test_content = Content(
        url="https://example.com",
        title="Test",
        content="Content",
        source="example.com",
        published_at=now,
        language="en",
        author="",
        summary="Test summary",
        topics=["topic1"],
        keywords=["key1"],
        sentiment="positive",
        reading_time=2
    )
    
    # Configure mocks
    mock_services["extractor"].extract_content.return_value = test_content
    mock_services["analyzer"].analyze_content.side_effect = ContentAnalysisError("Analysis failed")
    
    response = client.post(
        "/api/content/process",
        json={"url": "https://example.com"}
    )
    
    assert response.status_code == 422
    assert "Analysis failed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_process_multiple_urls_extraction_error(client, mock_services):
    """Test multiple URLs extraction error handling."""
    # Configure mock to raise ContentExtractionError
    mock_services["extractor"].extract_multiple.side_effect = ContentExtractionError("Failed to extract any content")
    
    response = client.post(
        "/api/content/process",
        json={"urls": ["https://example1.com", "https://example2.com"]}
    )
    
    assert response.status_code == 422
    assert "Failed to extract any content" in response.json()["detail"]


@pytest.mark.asyncio
async def test_process_multiple_urls_analysis_error(client, mock_services):
    """Test multiple URLs analysis error handling."""
    now = datetime.now()
    test_content = Content(
        url="https://example.com",
        title="Test",
        content="Content",
        source="example.com",
        published_at=now,
        language="en",
        author="",
        summary="Test summary",
        topics=["topic1"],
        keywords=["key1"],
        sentiment="positive",
        reading_time=2
    )
    
    # Configure mocks
    mock_services["extractor"].extract_multiple.return_value = [test_content]
    mock_services["analyzer"].analyze_multiple.side_effect = ContentAnalysisError("Analysis failed")
    
    response = client.post(
        "/api/content/process",
        json={"urls": ["https://example.com"]}
    )
    
    assert response.status_code == 422
    assert "Analysis failed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_process_url_validation_error(client, mock_services):
    """Test request validation error handling."""
    response = client.post(
        "/api/content/process",
        json={"url": "https://example.com", "urls": ["https://example.com"]}
    )
    
    assert response.status_code == 500
    assert "Exactly one of 'url' or 'urls' must be provided" in response.json()["detail"] 