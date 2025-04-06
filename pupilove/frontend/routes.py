import logging
import requests
import os
import starlette.status as status
from pathlib import Path
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
current_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=current_dir / "templates")
BACKEND_URL = os.getenv("BACKEND_URL")

# Due to lack of user authentication
DEFAULT_CREATOR_USER_ID = 6
DEFAULT_RESERVER_USER_ID = 4


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/test-db-connection", response_class=HTMLResponse)
def query_input_form(request: Request):
    return templates.TemplateResponse(
        "query_input.html", {"request": request, "result": None}
    )


@router.post("/test-db-connection", response_class=HTMLResponse)
def query_input(request: Request, query: str = Form(...)):
    response = requests.get(f"{BACKEND_URL}/execute-select", params={"query": query})
    if response.ok:
        result = response.json()
        return templates.TemplateResponse(
            "query_input.html", {"request": request, "result": result}
        )
    else:
        return RedirectResponse(
            url="/test-db-connection", status_code=status.HTTP_302_FOUND
        )


@router.get("/browse-listings", response_class=HTMLResponse)
def browse_listings(request: Request):
    response = requests.get(f"{BACKEND_URL}/active-listings")
    if response.ok:
        listing_data = response.json()
        return templates.TemplateResponse(
            "browse_listings.html", {"request": request, "listing_data": listing_data}
        )
    else:
        ...


@router.get("/listing/{listing_id}", response_class=HTMLResponse)
def listing(request: Request, listing_id: int):
    response = requests.get(f"{BACKEND_URL}//listing/{listing_id}")
    if response.ok:
        listing_data = response.json()
        return templates.TemplateResponse(
            "listing.html", {"request": request, "listing_data": listing_data}
        )
    else:
        ...


@router.post("/make-reservation/{listing_id}", response_class=HTMLResponse)
def make_reservation(request: Request, listing_id: int):
    data = {"reserver_user_id": DEFAULT_RESERVER_USER_ID}
    response = requests.post(f"{BACKEND_URL}/make-reservation/{listing_id}", json=data)
    if response.ok:
        result = response.json()
        position_in_queue = result["position_in_queue"]
        return templates.TemplateResponse(
            "make_reservation.html",
            {
                "request": request,
                "position_in_queue": position_in_queue,
                "success": True,
            },
        )
    else:
        error_message = response.json().get("detail", "An unknown error occurred")
        return templates.TemplateResponse(
            "make_reservation.html",
            {"request": request, "error_message": error_message, "success": False},
        )


@router.get("/my-listings", response_class=HTMLResponse)
def my_listings(request: Request):
    response = requests.get(f"{BACKEND_URL}/user-listings?creator_user_id={3}")
    if response.ok:
        listings = response.json()
        return templates.TemplateResponse(
            "my_listings.html",
            {"request": request, "listings": listings},
        )
