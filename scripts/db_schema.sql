CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_group ENUM('user', 'admin') NOT NULL
);

CREATE TABLE animal_categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    animal_type VARCHAR(255) NOT NULL
);

CREATE TABLE locations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    gps_coordinates VARCHAR(255)
);

CREATE TABLE listings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    creator_user_id INT NOT NULL,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    animal_category_id INT NOT NULL,
    age INT,
    location_id INT NOT NULL,
    description TEXT,
    status VARCHAR(255) DEFAULT 'active',
    FOREIGN KEY (creator_user_id) REFERENCES users(id),
    FOREIGN KEY (animal_category_id) REFERENCES animal_categories(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

CREATE TABLE images (
    id INT PRIMARY KEY AUTO_INCREMENT,
    listing_id INT NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    FOREIGN KEY (listing_id) REFERENCES listings(id)
);

CREATE TABLE reservations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    listing_id INT NOT NULL,
    reserver_user_id INT NOT NULL,
    status VARCHAR(255) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (listing_id) REFERENCES listings(id),
    FOREIGN KEY (reserver_user_id) REFERENCES users(id)
);
