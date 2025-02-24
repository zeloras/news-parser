"""Content extraction service."""
from datetime import datetime
from typing import List
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.models.content import Content
from src.core.exceptions import ContentExtractionError
from src.core.config import get_settings
from src.services.extraction.interface import ContentExtractorInterface

settings = get_settings()


class PlaywrightExtractor(ContentExtractorInterface):
    """Service for extracting content from web pages using Playwright."""

    def __init__(self):
        """Initialize the PlaywrightExtractor."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        return urlparse(url).netloc

    async def extract_content(self, url: str) -> Content:
        """Extract content from a URL."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(url)
                
                # Extract title and content
                title = await page.evaluate("document.title")
                content = await page.evaluate("""
                    Array.from(document.body.getElementsByTagName('*'))
                        .map(el => el.textContent)
                        .join('\\n')
                """)
                
                await browser.close()
                
                if not title or not content:
                    raise ContentExtractionError("Failed to extract content: Empty title or content")
                
                return Content(
                    url=url,
                    title=title,
                    content=content,
                    source=urlparse(url).netloc
                )
        except Exception as e:
            raise ContentExtractionError(f"Failed to extract content: {str(e)}")

    async def extract_multiple(self, urls: List[str]) -> List[Content]:
        """Extract content from multiple URLs."""
        contents = []
        for url in urls:
            try:
                content = await self.extract_content(url)
                contents.append(content)
            except Exception as e:
                pass
        return contents 