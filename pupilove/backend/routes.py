from fastapi import APIRouter, Depends, HTTPException
from database import get_db_connection
from fastapi.responses import JSONResponse

router = APIRouter()


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
