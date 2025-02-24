"""Tests for content extractor."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock, call
from src.services.extraction.extractor import PlaywrightExtractor
from src.core.exceptions import ContentExtractionError
from src.models.content import Content


@pytest.fixture
def extractor():
    """Create extractor instance with mocked dependencies."""
    with patch("src.services.extraction.extractor.RecursiveCharacterTextSplitter") as mock_splitter:
        # Configure text splitter mock
        mock_splitter.return_value = MagicMock()
        return PlaywrightExtractor()


@pytest.fixture
def mock_page():
    """Create mock page with default successful responses."""
    page = AsyncMock()
    
    # Create a mock evaluate function that returns different values based on input
    async def evaluate_mock(script):
        if script == "document.title":
            return "Test Title"
        elif "getElementsByTagName" in script:
            return "Test Content"
        return None
    
    page.evaluate = AsyncMock(side_effect=evaluate_mock)
    page.goto = AsyncMock()
    return page


@pytest.fixture
def mock_browser(mock_page):
    """Create mock browser that returns our mock page."""
    browser = AsyncMock()
    browser.new_page = AsyncMock(return_value=mock_page)
    browser.close = AsyncMock()
    return browser


@pytest.fixture
def mock_playwright_context(mock_browser):
    """Create mock playwright context."""
    context = MagicMock()
    context.chromium.launch = AsyncMock(return_value=mock_browser)
    return context


@pytest.fixture
def mock_playwright(mock_playwright_context):
    """Create mock playwright."""
    async def aenter():
        return mock_playwright_context
    
    async def aexit(*args):
        pass
    
    playwright = AsyncMock()
    playwright.__aenter__ = AsyncMock(side_effect=aenter)
    playwright.__aexit__ = AsyncMock(side_effect=aexit)
    return playwright


def test_initialization():
    """Test extractor initialization."""
    with patch("src.services.extraction.extractor.RecursiveCharacterTextSplitter") as mock_splitter:
        extractor = PlaywrightExtractor()
        assert mock_splitter.called
        assert extractor.text_splitter == mock_splitter.return_value


def test_extract_domain():
    """Test domain extraction from URL."""
    extractor = PlaywrightExtractor()
    test_cases = [
        ("https://example.com", "example.com"),
        ("http://sub.example.com/path", "sub.example.com"),
        ("https://example.com/path?query=1", "example.com"),
        ("http://example.com:8080", "example.com:8080")
    ]
    for url, expected in test_cases:
        assert extractor._extract_domain(url) == expected


@pytest.mark.asyncio
async def test_extract_content_success(extractor, mock_playwright):
    """Test successful content extraction."""
    with patch("src.services.extraction.extractor.async_playwright", return_value=mock_playwright):
        content = await extractor.extract_content("https://example.com")
        
        assert content.url == "https://example.com"
        assert content.title == "Test Title"
        assert content.content == "Test Content"
        assert content.source == "example.com"


@pytest.mark.asyncio
async def test_extract_content_empty_title(extractor, mock_playwright, mock_page):
    """Test content extraction with empty title."""
    async def evaluate_mock(script):
        if script == "document.title":
            return ""  # Empty title
        elif "getElementsByTagName" in script:
            return "Test Content"
        return None
    
    mock_page.evaluate = AsyncMock(side_effect=evaluate_mock)
    
    with patch("src.services.extraction.extractor.async_playwright", return_value=mock_playwright):
        with pytest.raises(ContentExtractionError, match="Failed to extract content: Empty title or content"):
            await extractor.extract_content("https://example.com")


@pytest.mark.asyncio
async def test_extract_content_empty_content(extractor, mock_playwright, mock_page):
    """Test content extraction with empty content."""
    async def evaluate_mock(script):
        if script == "document.title":
            return "Test Title"
        elif "getElementsByTagName" in script:
            return ""  # Empty content
        return None
    
    mock_page.evaluate = AsyncMock(side_effect=evaluate_mock)
    
    with patch("src.services.extraction.extractor.async_playwright", return_value=mock_playwright):
        with pytest.raises(ContentExtractionError, match="Failed to extract content: Empty title or content"):
            await extractor.extract_content("https://example.com")


@pytest.mark.asyncio
async def test_extract_content_page_error(extractor, mock_playwright, mock_page):
    """Test content extraction when page evaluation fails."""
    async def evaluate_mock(script):
        raise Exception("Failed to evaluate page")
    
    mock_page.evaluate = AsyncMock(side_effect=evaluate_mock)
    
    with patch("src.services.extraction.extractor.async_playwright", return_value=mock_playwright):
        with pytest.raises(ContentExtractionError, match="Failed to extract content: Failed to evaluate page"):
            await extractor.extract_content("https://example.com")


@pytest.mark.asyncio
async def test_extract_content_browser_error(extractor):
    """Test content extraction when browser launch fails."""
    async def aenter():
        raise Exception("Browser error")
    
    mock_playwright = AsyncMock()
    mock_playwright.__aenter__ = AsyncMock(side_effect=aenter)
    mock_playwright.__aexit__ = AsyncMock()
    
    with patch("src.services.extraction.extractor.async_playwright", return_value=mock_playwright):
        with pytest.raises(ContentExtractionError, match="Failed to extract content: Browser error"):
            await extractor.extract_content("https://example.com")


@pytest.mark.asyncio
async def test_extract_multiple_success(extractor):
    """Test successful extraction of multiple URLs."""
    urls = ["https://example1.com", "https://example2.com"]
    test_content = Content(
        url="https://example1.com",
        title="Test Title",
        content="Test Content",
        source="example1.com"
    )
    
    with patch.object(extractor, "extract_content") as mock_extract:
        mock_extract.side_effect = [test_content, test_content]
        
        contents = await extractor.extract_multiple(urls)
        assert len(contents) == 2
        assert all(c.url.startswith("https://example") for c in contents)
        assert mock_extract.call_count == 2


@pytest.mark.asyncio
async def test_extract_multiple_partial_failure(extractor):
    """Test multiple URL extraction with some failures."""
    urls = ["https://example1.com", "https://example2.com", "https://example3.com"]
    test_content = Content(
        url="https://example1.com",
        title="Test Title",
        content="Test Content",
        source="example1.com"
    )
    
    with patch.object(extractor, "extract_content") as mock_extract:
        mock_extract.side_effect = [
            test_content,
            ContentExtractionError("Failed"),
            test_content
        ]
        
        contents = await extractor.extract_multiple(urls)
        assert len(contents) == 2  # One failed, two succeeded
        assert mock_extract.call_count == 3


@pytest.mark.asyncio
async def test_extract_multiple_all_fail(extractor):
    """Test multiple URL extraction when all fail."""
    urls = ["https://example1.com", "https://example2.com"]
    
    with patch.object(extractor, "extract_content") as mock_extract:
        mock_extract.side_effect = ContentExtractionError("Failed")
        
        contents = await extractor.extract_multiple(urls)
        assert len(contents) == 0
        assert mock_extract.call_count == 2 