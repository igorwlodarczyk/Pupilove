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
    response = requests.get(
        f"{BACKEND_URL}/user-listings?creator_user_id={DEFAULT_CREATOR_USER_ID}"
    )
    if response.ok:
        listings = response.json()
        return templates.TemplateResponse(
            "my_listings.html",
            {"request": request, "listings": listings},
        )


@router.post(
    "/reservation-decision/{reservation_id}/{decision}", response_class=HTMLResponse
)
def reservation_decision(request: Request, reservation_id: int, decision: str):
    response = requests.post(
        f"{BACKEND_URL}//make-decision/{reservation_id}/{decision}"
    )
    if response.ok:
        return templates.TemplateResponse(
            "reservation_decision.html",
            {"request": request, "decision": decision},
        )
    else:
        ...


@router.get("/my-reservations", response_class=HTMLResponse)
def my_reservation(request: Request):
    response = requests.get(
        f"{BACKEND_URL}/user-reservations?reserver_user_id={DEFAULT_RESERVER_USER_ID}"
    )
    if response.ok:
        reservations = response.json()
        return templates.TemplateResponse(
            "my_reservations.html",
            {"request": request, "reservations": reservations},
        )
    else:
        ...


# WYSZUKIWANIE LISTINGOW
@router.get("/search-listings", response_class=HTMLResponse)
def search_listings(request: Request):
    # pobieramy kategorie zwierzat jakie sa
    response = requests.get(f"{BACKEND_URL}/get-animal-categories")
    if response.ok:
        # Trzeba napisac template ktory ma w sobie formularz html
        # gdzie uzytkownik moze wpisac slowo kluczowe i zaznaczyc z dostepnych kategorii
        # jakie zwierzeta go interesuja
        # nastepnie jak przycisnie przycisk Search
        # to ma go wyslac POST na /search-listings
        animal_categories = response.json()
        templates.TemplateResponse(
            "search_listings.html",
            {"request": request, "animal_categories": animal_categories},
        )


@router.post("/search-listings", response_class=HTMLResponse)
def search_listings_result(
    request: Request,
    keyword: str = Form(""),
    selected_categories: list[str] = Form([]),
):
    # Odczytujemy dane z formularza
    payload = {"keyword": keyword, "categories": selected_categories}

    # Pobieramy dane z naszego wyszukiwania
    response = requests.post(f"{BACKEND_URL}/search-listings", json=payload)

    if response.ok:
        search_results = response.json()
    else:
        search_results = []

    # Trzeba napisac template ktory wyswietli te dane
    return templates.TemplateResponse(
        "search_results.html",
        {
            "request": request,
            "results": search_results,
            "keyword": keyword,
            "selected_categories": selected_categories,
        },
    )


# Dodanie ogloszenia
@router.get("/add-listing", response_class=HTMLResponse)
def add_listing(request: Request):
    # Trzeba napisac template add_listing ktory ma formularz
    # gdzie uzytkownik moze wpisac dane swojego ogloszenia

    response = requests.get(f"{BACKEND_URL}/get-animal-categories")
    if response.ok:
        animal_categories = response.json()
        # uzytkownik zaznacza kategorie zwierzaka ogloszenia
        # musi byc przycisk ADD w formularzu ktory wysyla request POST do /add-listing
        return templates.TemplateResponse(
            "add_listing.html",
            {"request": request, "animal_categories": animal_categories},
        )
    else:
        ...


@router.post("/add-listing", response_class=HTMLResponse)
def post_add_listing(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    animal_category_id: int = Form(...),
):
    # user id jak wysylamy request to bierzemy to
    user_id = DEFAULT_CREATOR_USER_ID
    # jest to uproszczenie bo nie mamy logowania zrobionego
    payload = {
        "title": title,
        "description": description,
        "animal_category_id": animal_category_id,
        "creator_user_id": user_id,
    }

    response = requests.post(f"{BACKEND_URL}/add-listing", json=payload)

    if response.ok:
        # przekierowanie do /my-listings
        ...
    else:
        ...
