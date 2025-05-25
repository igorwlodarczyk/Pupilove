import uuid
import random

CREATOR_USER_ID = 3
RESERVER_USER_ID = 1
NUMBER_OF_LOCATIONS = 25_000
NUMBER_OF_LISTINGS = 5_000


def generate_locations(number_of_locations: int) -> str:
    query_str = "INSERT INTO locations (name, gps_coordinates) VALUES "
    for location_idx in range(number_of_locations):
        name = uuid.uuid4()
        gps_coordinates = uuid.uuid4()
        query_str += f"('{name}', '{gps_coordinates}'), "
    query_str = query_str[:-2] + ";"
    return query_str


def generate_listings(number_of_listings: int) -> str:
    query_str = "INSERT INTO listings (title, creator_user_id, animal_category_id, age, location_id, description) VALUES "
    for listing_idx in range(number_of_listings):
        title = uuid.uuid4()
        creator_user_id = CREATOR_USER_ID
        animal_category_id = random.randint(1, 20)
        age = random.randint(1, 20)
        location_id = random.randint(1, NUMBER_OF_LOCATIONS)
        description = uuid.uuid4()

        query_str += f"('{title}', {creator_user_id}, {animal_category_id}, {age}, {location_id}, '{description}'), "

    query_str = query_str.rstrip(", ") + ";"
    return query_str


def generate_reservations() -> str:
    query_str = "INSERT INTO reservations (listing_id, reserver_user_id) VALUES "
    for listing_idx in range(NUMBER_OF_LISTINGS):
        if listing_idx % 3 == 0:
            listing_id = listing_idx + 1
            query_str += f"({listing_id}, {RESERVER_USER_ID}), "
    query_str = query_str.rstrip(", ") + ";"
    return query_str


with open("test_data.sql", "w") as test_data_sql:
    locations = generate_locations(number_of_locations=NUMBER_OF_LOCATIONS)
    test_data_sql.write(locations + "\n")
    listings = generate_listings(number_of_listings=NUMBER_OF_LISTINGS)
    test_data_sql.write(listings + "\n")
    reservations = generate_reservations()
    test_data_sql.write(reservations + "\n")
