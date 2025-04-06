import requests
import starlette.status as status
from pathlib import Path
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates


router = APIRouter()
current_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=current_dir / "templates")
BASE_URL = "http://localhost:8000"

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/test-db-connection", response_class=HTMLResponse)
def query_input_form(request: Request):
    return templates.TemplateResponse(
        "query_input.html", {"request": request, "result": None}
    )


@router.post("/test-db-connection", response_class=HTMLResponse)
def query_input(
    request: Request, query: str = Form(...)
):
    response = requests.get(f"{BASE_URL}/execute-select", params={"query": query})
    if response.ok:
        result = response.json()
        return templates.TemplateResponse(
            "query_input.html", {"request": request, "result": result}
        )
    else:
        return RedirectResponse(url="/test-db-connection", status_code=status.HTTP_302_FOUND)

