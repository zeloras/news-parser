"""Tests for content analyzer."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.analysis.analyzer import OpenAIAnalyzer
from src.models.content import Content
from src.models.analysis import ContentAnalysis
from src.core.exceptions import ContentAnalysisError


@pytest.fixture
def analyzer():
    """Create analyzer instance with mocked dependencies."""
    with patch("src.services.analysis.analyzer.ChatOpenAI") as mock_chat, \
         patch("src.services.analysis.analyzer.RecursiveCharacterTextSplitter") as mock_splitter, \
         patch("src.services.analysis.analyzer.PydanticOutputParser") as mock_parser, \
         patch("src.services.analysis.analyzer.ChatPromptTemplate") as mock_prompt:
        
        # Configure mocks
        mock_chat.return_value = MagicMock()
        text_splitter = MagicMock()
        text_splitter.split_text = MagicMock(return_value=["Test chunk"])
        mock_splitter.return_value = text_splitter
        
        mock_parser.return_value = MagicMock(
            parse=lambda x: ContentAnalysis(
                title="Test Title",
                summary="Test summary",
                topics=["topic1", "topic2"],
                sentiment="positive",
                keywords=["key1", "key2"],
                reading_time=5,
                author="Test Author"
            )
        )
        mock_prompt.from_template.return_value = MagicMock()
        
        analyzer = OpenAIAnalyzer()
        analyzer.analysis_chain = AsyncMock()
        analyzer.analysis_chain.ainvoke.return_value = MagicMock(
            content="summary: Test summary\ntopics: topic1, topic2\nsentiment: positive\nkeywords: key1, key2\nreading_time: 5\nauthor: Test Author"
        )
        
        return analyzer


@pytest.fixture
def test_content():
    """Create test content."""
    return Content(
        url="https://example.com",
        title="Test Title",
        content="Test content for analysis",
        source="example.com",
        summary="Test summary",
        topics=["topic1", "topic2"],
        keywords=["key1", "key2"],
        sentiment="positive",
        reading_time=5,
        author="Test Author"
    )


@pytest.mark.asyncio
async def test_analyze_content_success(analyzer):
    """Test successful content analysis."""
    content = Content(
        url="http://test.com",
        title="Test",
        content="Test content",
        source="test.com"
    )
    result = await analyzer.analyze_content(content)
    
    assert result.summary == "Test summary"
    assert result.topics == ["topic1", "topic2"]
    assert result.sentiment == "positive"
    assert result.keywords == ["key1", "key2"]
    assert result.reading_time == 5
    assert result.author == "Test Author"


@pytest.mark.asyncio
async def test_analyze_content_no_chunks(analyzer):
    """Test content analysis when no chunks are produced."""
    analyzer.text_splitter.split_text = MagicMock(return_value=[])
    content = Content(
        url="http://test.com",
        title="Test",
        content="Test content",
        source="test.com"
    )
    
    with pytest.raises(ContentAnalysisError, match="No content to analyze"):
        await analyzer.analyze_content(content)


@pytest.mark.asyncio
async def test_analyze_content_no_analysis_result(analyzer):
    """Test content analysis when chain produces no results."""
    analyzer.analysis_chain.ainvoke.return_value = None
    content = Content(
        url="http://test.com",
        title="Test",
        content="Test content",
        source="test.com"
    )
    
    with pytest.raises(ContentAnalysisError, match="Analysis produced no results"):
        await analyzer.analyze_content(content)


@pytest.mark.asyncio
async def test_analyze_content_chain_error(analyzer):
    """Test content analysis when chain raises an error."""
    analyzer.analysis_chain.ainvoke.side_effect = Exception("Chain error")
    content = Content(
        url="http://test.com",
        title="Test",
        content="Test content",
        source="test.com"
    )
    
    with pytest.raises(ContentAnalysisError, match="Content analysis failed: Chain error"):
        await analyzer.analyze_content(content)


@pytest.mark.asyncio
async def test_analyze_multiple_success(analyzer):
    """Test successful analysis of multiple contents."""
    contents = [
        Content(
            url="http://test1.com",
            title="Test 1",
            content="Test content 1",
            source="test1.com"
        ),
        Content(
            url="http://test2.com",
            title="Test 2",
            content="Test content 2",
            source="test2.com"
        )
    ]
    results = await analyzer.analyze_multiple(contents)
    
    assert len(results) == 2
    assert all(r.summary == "Test summary" for r in results)
    assert all(r.topics == ["topic1", "topic2"] for r in results)


@pytest.mark.asyncio
async def test_analyze_multiple_partial_failure(analyzer):
    """Test multiple content analysis with some failures."""
    contents = [
        Content(
            url="http://test1.com",
            title="Test 1",
            content="Test content 1",
            source="test1.com"
        ),
        Content(
            url="http://test2.com",
            title="Test 2",
            content="Test content 2",
            source="test2.com"
        ),
        Content(
            url="http://test3.com",
            title="Test 3",
            content="Test content 3",
            source="test3.com"
        )
    ]
    
    analyzer.analysis_chain.ainvoke.side_effect = [
        MagicMock(content="summary: Test\ntopics: test\nsentiment: positive\nkeywords: test\nreading_time: 5"),
        Exception("Failed"),
        MagicMock(content="summary: Test\ntopics: test\nsentiment: positive\nkeywords: test\nreading_time: 5")
    ]
    
    results = await analyzer.analyze_multiple(contents)
    assert len(results) == 2  # One failed, two succeeded


@pytest.mark.asyncio
async def test_analyze_multiple_all_fail(analyzer):
    """Test multiple content analysis when all fail."""
    analyzer.analysis_chain.ainvoke.side_effect = Exception("Failed")
    contents = [
        Content(
            url="http://test1.com",
            title="Test 1",
            content="Test content 1",
            source="test1.com"
        ),
        Content(
            url="http://test2.com",
            title="Test 2",
            content="Test content 2",
            source="test2.com"
        )
    ]
    
    with pytest.raises(ContentAnalysisError, match="Failed to analyze any content"):
        await analyzer.analyze_multiple(contents)


@pytest.mark.asyncio
async def test_analyze_multiple(analyzer, test_content):
    """Test analyzing multiple content items."""
    contents = [test_content, test_content]
    
    with patch.object(analyzer, "analyze_content") as mock_analyze:
        mock_analyze.side_effect = [
            AsyncMock(return_value=test_content),
            AsyncMock(return_value=test_content)
        ]
        
        results = await analyzer.analyze_multiple(contents)
        assert len(results) == 2
        assert mock_analyze.call_count == 2 