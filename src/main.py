"""Main application module."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.core.config import get_settings
from src.api.routes import content, search
from src.web.routes import router as web_router

settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version
)

# Mount static files
app.mount("/static", StaticFiles(directory="./src/web/static"), name="static")

# Include routers
app.include_router(web_router)  # Web interface routes
app.include_router(content.router)  # API routes for content operations
app.include_router(search.router)  # API routes for search
