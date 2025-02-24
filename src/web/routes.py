"""Web interface routes."""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="src/web/templates")

router = APIRouter()


@router.get("/")
async def index(request: Request):
    """Render index page."""
    return templates.TemplateResponse("index.html", {"request": request}) 