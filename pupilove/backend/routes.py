import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime
from database import get_db_connection
from fastapi.responses import JSONResponse

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/execute-select", response_class=JSONResponse)
def query_input_form(query: str, db=Depends(get_db_connection)):
    return db.execute_select(query)


@router.get("/active-listings", response_class=JSONResponse)
def get_active_listings(db=Depends(get_db_connection)):
    query = """
        SELECT 
            listings.id, 
            listings.title, 
            listings.creator_user_id, 
            listings.published_at, 
            listings.animal_category_id, 
            listings.age, 
            listings.location_id, 
            listings.description, 
            listings.status, 
            locations.name AS location_name, 
            animal_categories.animal_type,
            users.username AS creator_user_name
        FROM 
            listings
        JOIN 
            locations ON listings.location_id = locations.id
        JOIN 
            animal_categories ON listings.animal_category_id = animal_categories.id
        JOIN
            users ON listings.creator_user_id = users.id
        WHERE 
            listings.status = 'active';
    """
    return db.execute_select(query)


@router.get("/listing/{listing_id}", response_class=JSONResponse)
def get_listing_data(listing_id: int, db=Depends(get_db_connection)):
    query = """
        SELECT 
            listings.id, 
            listings.title, 
            listings.creator_user_id, 
            listings.published_at, 
            listings.animal_category_id, 
            listings.age, 
            listings.location_id, 
            listings.description, 
            listings.status, 
            locations.name AS location_name, 
            users.username AS creator_user_name 
        FROM 
            listings
        JOIN 
            locations ON listings.location_id = locations.id
        JOIN 
            users ON listings.creator_user_id = users.id
        WHERE 
            listings.id = %s;
    """
    params = (listing_id,)
    listing_data = db.execute_select(query, params)[0]
    return listing_data


@router.post("/make-reservation/{listing_id}", response_class=JSONResponse)
def create_reservation(
    listing_id: int, reservation: dict, db=Depends(get_db_connection)
):
    if "reserver_user_id" not in reservation:
        raise HTTPException(status_code=400, detail="Not logged in.")

    status_query = "SELECT status FROM listings WHERE id = %s;"
    status_result = db.execute_select(status_query, (listing_id,))

    if not status_result or status_result[0]["status"] != "active":
        raise HTTPException(
            status_code=400,
            detail="The listing is not available for reservation. It may not be active.",
        )

    reservation_check_query = """
        SELECT id FROM reservations 
        WHERE listing_id = %s AND reserver_user_id = %s;
        """
    reservation_check_params = (listing_id, reservation["reserver_user_id"])
    existing_reservation_check = db.execute_select(
        reservation_check_query, reservation_check_params
    )
    if len(existing_reservation_check) > 0:
        raise HTTPException(
            status_code=400,
            detail="You have already made a reservation for this listing.",
        )

    query = """
    INSERT INTO reservations (listing_id, reserver_user_id) 
    VALUES (%s, %s);
    """
    params = (
        listing_id,
        reservation["reserver_user_id"],
    )

    record_id = db.execute_insert(query, params)

    position_query = """
        SELECT COUNT(*) AS position_in_queue
        FROM reservations 
        WHERE listing_id = %s AND created_at <= (
            SELECT created_at 
            FROM reservations 
            WHERE id = %s
        );
        """
    position_params = (listing_id, record_id)
    position_result = db.execute_select(position_query, position_params)

    position_in_queue = position_result[0]["position_in_queue"]

    return {
        "message": "Reservation created successfully",
        "listing_id": listing_id,
        "reserver_user_id": reservation["reserver_user_id"],
        "record_id": record_id,
        "position_in_queue": position_in_queue,
    }


@router.get("/user-listings", response_class=JSONResponse)
def get_user_listings(creator_user_id: int, db=Depends(get_db_connection)):
    query = """
    SELECT 
        l.id AS listing_id,
        l.title,
        l.creator_user_id,
        l.published_at,
        l.animal_category_id,
        l.age,
        l.location_id,
        l.description,
        l.status,
        IF(COUNT(CASE WHEN r.status = 'pending' THEN 1 END) > 0, TRUE, FALSE) AS has_pending_reservations,
        (
        SELECT r2.id
        FROM reservations r2
        WHERE r2.listing_id = l.id AND r2.status = 'pending'
        ORDER BY r2.created_at ASC
        LIMIT 1
        ) AS reservation_id,
        (
            SELECT u.username 
            FROM reservations r2
            JOIN users u ON r2.reserver_user_id = u.id
            WHERE r2.listing_id = l.id AND r2.status = 'pending'
            ORDER BY r2.created_at ASC
            LIMIT 1
        ) AS reserver_username,
        (
            SELECT u.email 
            FROM reservations r2
            JOIN users u ON r2.reserver_user_id = u.id
            WHERE r2.listing_id = l.id AND r2.status = 'pending'
            ORDER BY r2.created_at ASC
            LIMIT 1
        ) AS reserver_email
    FROM 
        listings l
    LEFT JOIN 
        reservations r ON l.id = r.listing_id
    WHERE 
        l.creator_user_id = %s
    GROUP BY 
        l.id;
    """
    params = (creator_user_id,)
    result = db.execute_select(query, params)
    return result


@router.post("/make-decision/{reservation_id}/{decision}", response_class=JSONResponse)
def make_decision(reservation_id: int, decision: str, db=Depends(get_db_connection)):
    new_status = "accepted" if decision == "accept" else "declined"
    reservation_update_query = """
        UPDATE reservations
        SET status = %s
        WHERE id = %s AND status = 'pending';
        """
    affected_rows = db.execute_update(
        reservation_update_query, (new_status, reservation_id)
    )

    if affected_rows == 0:
        raise HTTPException(
            status_code=404, detail="Reservation not found or already processed."
        )

    get_listing_id_query = "SELECT listing_id FROM reservations WHERE id = %s;"

    listing_id = db.execute_select(get_listing_id_query, (reservation_id,))[0][
        "listing_id"
    ]

    if new_status == "accepted":
        listing_update_query = """
            UPDATE listings
            SET status = 'inactive'
            WHERE id = %s;
            """
        db.execute_update(listing_update_query, (listing_id,))

        decline_remaining_reservations_query = """
            UPDATE reservations
            SET status = 'declined'
            WHERE listing_id = %s
            AND status = 'pending' AND id != %s;
            """
        db.execute_update(
            decline_remaining_reservations_query, (listing_id, reservation_id)
        )
    return {"message": f"Decision '{new_status}' applied."}


@router.get("/user-reservations", response_class=JSONResponse)
def get_user_reservations(reserver_user_id: int, db=Depends(get_db_connection)):
    query = """
            SELECT r.id AS reservation_id,
                   r.listing_id,
                   r.reserver_user_id,
                   r.status AS reservation_status,
                   r.created_at AS reservation_created_at,
                   l.title AS listing_title,
                   l.status AS listing_status,
                   l.published_at AS listing_created_at
            FROM reservations r
            JOIN listings l ON r.listing_id = l.id
            WHERE r.reserver_user_id = %s;
        """
    params = (reserver_user_id,)
    result = db.execute_select(query, params)
    return {"reservations": result}

# WYSZUKIWANIE LISTINGOW
@router.get("/get-animal-categories", response_class=JSONResponse)
def get_animal_categories(db=Depends(get_db_connection)):
    """
    Trzeba napisac selecta ktory zwroci jakie sa kategorie zwierzat w bazie danych
    """
    query = """
            SELECT * FROM animal_categories;
        """
    result = db.execute_select(query)
    return result


@router.post("/search-listings", response_class=JSONResponse)
async def search_listings(request: Request, db=Depends(get_db_connection)):
    body = await request.json()
    keyword = body.get("keyword", "").strip()
    categories = body.get("categories", [])

    conditions = ["listings.status = 'active'"]
    params = []

    if keyword:
        conditions.append("(listings.title LIKE %s OR listings.description LIKE %s)")
        keyword_param = f"%{keyword}%"
        params.extend([keyword_param, keyword_param])

    if categories:
        placeholders = ', '.join(['%s'] * len(categories))
        conditions.append(f"listings.animal_category_id IN ({placeholders})")
        params.extend(categories)

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT 
            listings.id, 
            listings.title, 
            listings.creator_user_id, 
            listings.published_at, 
            listings.animal_category_id, 
            listings.age, 
            listings.location_id, 
            listings.description, 
            listings.status, 
            locations.name AS location_name, 
            animal_categories.animal_type,
            users.username AS creator_user_name
        FROM 
            listings
        JOIN 
            locations ON listings.location_id = locations.id
        JOIN 
            animal_categories ON listings.animal_category_id = animal_categories.id
        JOIN
            users ON listings.creator_user_id = users.id
        WHERE 
            {where_clause};
    """

    result = db.execute_select(query, tuple(params))
    return {"results": result}

@router.post("/add-listing", response_class=JSONResponse)
async def add_listing(request: Request, db=Depends(get_db_connection)):
    body = await request.json()

    title = body.get("title")
    description = body.get("description")
    animal_category_id = body.get("animal_category_id")
    creator_user_id = body.get("creator_user_id")
    age = body.get("age")
    location_id = body.get("location_id")

    if not all([title, description, animal_category_id, creator_user_id, location_id]):
        raise HTTPException(status_code=400, detail="Missing required fields.")

    query = """
        INSERT INTO listings 
        (title, description, animal_category_id, creator_user_id, age, location_id, status, published_at) 
        VALUES (%s, %s, %s, %s, %s, %s, 'active', %s);
    """
    params = (
        title,
        description,
        animal_category_id,
        creator_user_id,
        age,
        location_id,
        datetime.utcnow(),
    )

    listing_id = db.execute_insert(query, params)

    return {
        "message": "Listing created successfully.",
        "listing_id": listing_id,
        "title": title,
        "status": "active"
    }
