from pathlib import Path
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from database import get_db_connection

router = APIRouter()
current_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=current_dir / "templates")


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
    request: Request, query: str = Form(...), db=Depends(get_db_connection)
):
    result = db.execute_select(query)
    return templates.TemplateResponse(
        "query_input.html", {"request": request, "result": result}
    )
