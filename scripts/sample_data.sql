-- Example data
INSERT INTO users (username, hashed_password, email, user_group) VALUES
('default_reserver_user_1', 'secret_password', 'default_reserver_user_1@example.com', 'user'),
('big_man_admin', 'admin', 'admin@pupilove.com', 'admin'),
('default_creator_user_1', 'abc123', 'default_creator_user_1@example.com', 'user'),
('default_reserver_user_2', 'xd123', 'default_reserver_user_2@example.com', 'user'),
('default_reserver_user_3', '2000dog', 'default_reserver_user_3@example.com', 'user'),
('default_creator_user_2', 'dddd300', 'default_creator_user_2@example.com', 'user');

INSERT INTO animal_categories (animal_type) VALUES
('Dog'),
('Cat'),
('Rabbit'),
('Hamster'),
('Guinea Pig'),
('Bird'),
('Fish'),
('Turtle'),
('Lizard'),
('Snake'),
('Ferret'),
('Horse'),
('Goat'),
('Pig'),
('Chicken'),
('Duck'),
('Frog'),
('Chinchilla'),
('Hedgehog'),
('Mouse');

INSERT INTO locations (name, gps_coordinates) VALUES
('New York', '40.7128,-74.0060'),
('Los Angeles', '34.0522,-118.2437'),
('Sosnowiec', '50.2868,19.1048'),
('Boat city', '51.7592,19.4560'),
('Walbrzych', '50.7722,16.2833'),
('Mielno', '54.3000,16.0200');

INSERT INTO listings (title, creator_user_id, animal_category_id, age, location_id, description) VALUES
('Bark Vader', 3, 1, 5, 3, 'May the paws be with you. This dog has an undeniable presence. Beware of his epic howls.'),
('Paw-some Explorer', 6, 1, 3, 5, 'This adventurous dog loves exploring new places. Ready for outdoor fun!'),
('Whisker Wizard', 3, 2, 4, 4, 'This cat will cast a spell on your heart, but also on your furniture. Expect mysterious claw marks.');

INSERT INTO reservations (listing_id, reserver_user_id) VALUES
(1, 1),
(1, 4);