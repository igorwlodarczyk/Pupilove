-- Example data
INSERT INTO users (username, hashed_password, email, user_group) VALUES
('john_doe', 'hashedpassword123', 'john@example.com', 'user'),
('jane_smith', 'hashedpassword456', 'jane@example.com', 'admin'),
('alice_wonder', 'hashedpassword789', 'alice@example.com', 'user'),
('bob_builder', 'hashedpassword101', 'bob@example.com', 'user');

INSERT INTO animal_categories (animal_type) VALUES
('Dog'),
('Cat'),
('Bird');

INSERT INTO locations (name, gps_coordinates) VALUES
('New York', '40.7128,-74.0060'),
('Los Angeles', '34.0522,-118.2437');

INSERT INTO listings (title, creator_user_id, animal_category_id, age, location_id, description) VALUES
('Uncommon dog', 2, 1, 2, 1, 'Describtion one'),
('Rare Cat', 2, 2, 3, 2, 'Other Describtion');

INSERT INTO images (listing_id, image_path) VALUES
(1, '/images/dog.jpg'),
(2, '/images/cat.jpg');

INSERT INTO reservations (listing_id, reserver_user_id) VALUES
(1, 3),
(2, 4);