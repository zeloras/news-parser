"""Application configuration."""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.0"))
    
    # Database Configuration
    chroma_persist_dir: str = os.getenv("PERSIST_DIRECTORY", "./data/chroma")
    
    # API Configuration
    api_title: str = os.getenv("API_TITLE", "Content Processing API")
    api_description: str = os.getenv("API_DESCRIPTION", "API for extracting, analyzing and searching web content")
    api_version: str = os.getenv("API_VERSION", "1.0.0")
    
    # Content Extraction Configuration
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "2000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    max_results: int = int(os.getenv("MAX_RESULTS", "5"))


def get_settings() -> Settings:
    """Get application settings."""
    return Settings() 