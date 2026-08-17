from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from darknight.services.config.settings import get_app_config
from darknight.templates import render_template

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def base():
    return render_template(get_app_config().templates.home_page)
