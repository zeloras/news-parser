"""Content storage service."""
from typing import List
from pathlib import Path
import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from src.models.content import Content
from src.core.exceptions import DatabaseError, SearchError
from src.core.config import get_settings
from src.services.storage.interface import ContentRepositoryInterface

settings = get_settings()


class ChromaRepository(ContentRepositoryInterface):
    """Service for storing and retrieving content using ChromaDB."""
    
    def __init__(self, persist_dir: str = None):
        """Initialize the ChromaRepository."""
        self.persist_dir = persist_dir or settings.chroma_persist_dir
        
        # Initialize text splitter for proper chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            api_key=settings.openai_api_key
        )
        
        try:
            # Create persist directory if it doesn't exist
            Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)
            
            # Initialize LangChain's Chroma with the client and collection name
            self.vectorstore = Chroma(
                collection_name="content",
                embedding_function=self.embeddings,
                client=self.chroma_client
            )
            
            # Initialize retriever
            self.retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": settings.max_results}
            )
            
        except Exception as e:
            raise DatabaseError(f"Vector store initialization failed: {str(e)}")

    def _create_document(self, content: Content) -> List[Document]:
        """Create document for vector store."""
        # Create document text combining important fields
        doc_text = f"""Title: {content.title}
        Summary: {content.summary}
        Topics: {', '.join(content.topics)}
        Keywords: {', '.join(content.keywords)}
        Content: {content.content}"""
        
        # Split into chunks
        chunks = self.text_splitter.split_text(doc_text)
        
        # Create documents with metadata
        return [
            Document(
                page_content=chunk,
                metadata={
                    "url": content.url,
                    "title": content.title,
                    "source": content.source,
                    "summary": content.summary,
                    "content": content.content,
                    "author": content.author,
                    "published_at": str(content.published_at),
                    "language": content.language,
                    "sentiment": content.sentiment,
                    "reading_time": content.reading_time,
                    "topics": ", ".join(content.topics),
                    "keywords": ", ".join(content.keywords)
                }
            ) for chunk in chunks
        ]

    async def store(self, content: Content) -> None:
        """Store content in database."""
        try:
            documents = self._create_document(content)
            self.vectorstore.add_documents(documents)
        except Exception as e:
            raise DatabaseError(f"Document storage failed: {str(e)}")

    async def store_multiple(self, contents: List[Content]) -> None:
        """Store multiple content items in database."""
        try:
            all_documents = []
            for content in contents:
                documents = self._create_document(content)
                all_documents.extend(documents)
            
            if all_documents:
                self.vectorstore.add_documents(all_documents)
        except Exception as e:
            raise DatabaseError(f"Batch document storage failed: {str(e)}")

    async def search(self, query: str, limit: int = None) -> List[Content]:
        """Search content in database."""
        try:
            # Get relevant documents using similarity search
            relevant_docs = self.vectorstore.similarity_search(
                query=query,
                k=limit or settings.max_results
            )
            
            if not relevant_docs:
                return []
            
            # Get unique content items from metadata
            seen_urls = set()
            contents = []
            
            for doc in relevant_docs:
                url = doc.metadata.get("url")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    contents.append(Content(
                        url=url,
                        title=doc.metadata.get("title", ""),
                        source=doc.metadata.get("source", ""),
                        content=doc.metadata.get("content", ""),
                        summary=doc.metadata.get("summary", ""),
                        author=doc.metadata.get("author", ""),
                        published_at=doc.metadata.get("published_at", ""),
                        language=doc.metadata.get("language", ""),
                        sentiment=doc.metadata.get("sentiment", "neutral"),
                        reading_time=doc.metadata.get("reading_time", 0),
                        topics=doc.metadata.get("topics", "").split(", ") if doc.metadata.get("topics") else [],
                        keywords=doc.metadata.get("keywords", "").split(", ") if doc.metadata.get("keywords") else []
                    ))
            
            return contents
            
        except Exception as e:
            raise SearchError(f"Search failed: {str(e)}") 