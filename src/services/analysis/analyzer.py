"""Content analysis service."""
from typing import List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain.output_parsers import PydanticOutputParser

from src.models.content import Content
from src.models.analyze import ContentAnalysis
from src.core.exceptions import ContentAnalysisError
from src.core.config import get_settings
from src.services.analysis.interface import ContentAnalyzerInterface

settings = get_settings()


class OpenAIAnalyzer(ContentAnalyzerInterface):
    """Service for analyzing content using OpenAI models."""

    def __init__(self):
        """Initialize the OpenAIAnalyzer."""
        self.llm = ChatOpenAI(
            model_name=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.parser = PydanticOutputParser(pydantic_object=ContentAnalysis)
        self.analysis_chain = self._create_analysis_chain()

    def _create_analysis_chain(self):
        """Create the analysis chain."""
        template = """Analyze the provided content and extract key information.
            Please provide a comprehensive analysis including:
            1. A concise summary capturing the main points
            2. Main topics discussed
            3. Overall sentiment
            4. Author name if mentioned
            5. Key terms and phrases

            {format_instructions}

            Content text:
            {text}
        """

        prompt = ChatPromptTemplate.from_template(template)
        
        return (
            {"text": RunnablePassthrough(), "format_instructions": lambda _: self.parser.get_format_instructions()}
            | prompt 
            | self.llm
        )

    async def analyze_content(self, content: Content) -> Content:
        """Analyze content using LLM."""
        try:
            # Split and take first chunk (most important content)
            chunks = self.text_splitter.split_text(content.content)
            if not chunks:
                raise ContentAnalysisError("No content to analyze")
            
            main_chunk = chunks[0]
            
            # Run analysis and parse result
            result = await self.analysis_chain.ainvoke(main_chunk)
            if not result or not result.content:
                raise ContentAnalysisError("Analysis produced no results")
            
            analysis = self.parser.parse(result.content)
            
            # Update content with analysis results
            content.summary = analysis.summary
            content.topics = analysis.topics
            content.sentiment = analysis.sentiment
            content.keywords = analysis.keywords
            content.reading_time = analysis.reading_time
            if analysis.author:
                content.author = analysis.author
            
            return content
            
        except Exception as e:
            raise ContentAnalysisError(f"Content analysis failed: {str(e)}")

    async def analyze_multiple(self, contents: List[Content]) -> List[Content]:
        """Analyze multiple content items."""
        analyzed_contents = []
        for content in contents:
            try:
                analyzed = await self.analyze_content(content)
                analyzed_contents.append(analyzed)
            except ContentAnalysisError as e:
                continue
        
        if not analyzed_contents:
            raise ContentAnalysisError("Failed to analyze any content")
        
        return analyzed_contents 