CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone_number VARCHAR(20),    
    password_hash VARCHAR(255) NOT NULL,
    prefers_pets boolean default FALSE,
    prefers_social_lifestyle boolean default FALSE,
    description TEXT,    
    role ENUM('admin', 'sharer', 'seeker') NOT NULL DEFAULT 'seeker',    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE properties (
    property_id INT AUTO_INCREMENT PRIMARY KEY,
    sharer_id INT NOT NULL,    
    address VARCHAR(255) NOT NULL,
    suburb VARCHAR(100),
    state VARCHAR(100),    
    bedrooms INT,
    bathrooms INT,    
    pet_friendly BOOLEAN DEFAULT FALSE,
    lifestyle_type ENUM('quiet', 'social') DEFAULT 'social',
    property_type ENUM('house', 'apartment', 'unit', 'granny_flat') DEFAULT 'house',   
    image_url VARCHAR(255),    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    
    FOREIGN KEY (sharer_id) REFERENCES users(user_id)
);

CREATE TABLE listings (
    listing_id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    weekly_price DECIMAL(10,2) NOT NULL,
    bills_included BOOLEAN DEFAULT FALSE,
    available_rooms INT DEFAULT 1,
    preferred_gender ENUM('male','female','any') DEFAULT 'any',
    availability_status ENUM('available', 'pending', 'occupied') DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(property_id)
);

CREATE TABLE saved_listings (
    favourite_id INT AUTO_INCREMENT PRIMARY KEY,    
    user_id INT NOT NULL,
    listing_id INT NOT NULL,    
    date_saved TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,    
    sender_id INT NOT NULL,
    listing_id INT NOT NULL,    
    message TEXT NOT NULL,    
    status ENUM('new', 'responded', 'closed') DEFAULT 'new',    
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP    
);

CREATE TABLE reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,    
    user_id INT NOT NULL,
    listing_id INT NOT NULL,    
    rating INT CHECK (rating >= 1 AND rating <= 5),    
    comment TEXT,    
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id)
);

CREATE TABLE documents (
    document_id INT AUTO_INCREMENT PRIMARY KEY,    
    listing_id INT NOT NULL,    
    doc_type VARCHAR(100),    
    file_url VARCHAR(255),    
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id)
);

CREATE TABLE applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,    
    seeker_id INT NOT NULL,
    listing_id INT NOT NULL,    
    introduction_message TEXT,   
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users
(full_name, email, phone_number, password_hash, description, role)
VALUES
('Admin One', 'admin@test.com', '0400000001', 'hashed_password', 'System admin', 'admin'),
('Admin Two', 'admin2@test.com', '0400000001', 'hashed_password', 'System admin', 'admin'),
('Homer Simpson', 'seller1@test.com', '0400000002', 'hashed_password', 'Property owner in Brisbane', 'sharer'),
('Marge Simpson', 'seller2@test.com', '0400000003', 'hashed_password', 'Looking for reliable tenants', 'sharer'),
('Lisa Simpson', 'buyer1@test.com', '0400000004', 'hashed_password', 'University student', 'seeker'),
('Bart Simpson', 'buyer2@test.com', '0400000005', 'hashed_password', 'Young professional', 'seeker');

INSERT INTO properties
(sharer_id, address, suburb, state, bedrooms, bathrooms, pet_friendly, lifestyle_type, property_type, image_url)
VALUES

-- Apartments
(3, '12 Queen Street', 'Brisbane CBD', 'QLD', 2, 1, TRUE, 'social', 'apartment', 'apartment.jpg'),
(3, '55 Adelaide Street', 'Brisbane CBD', 'QLD', 1, 1, FALSE, 'social', 'apartment', 'House1.jpg'),
(4, '8 Wharf Road', 'Surfers Paradise', 'QLD', 3, 2, TRUE, 'social', 'apartment', 'House2.jpg'),
(4, '102 River Terrace', 'South Brisbane', 'QLD', 2, 2, FALSE, 'quiet', 'apartment', 'House3.jpg'),
(3, '77 Eagle Street', 'Brisbane CBD', 'QLD', 1, 1, TRUE, 'quiet', 'apartment', 'apartment.jpg'),

-- Houses
(4, '25 Palm Avenue', 'Redcliffe', 'QLD', 4, 2, TRUE, 'social', 'house', 'grannyflathome.jpg'),
(3, '9 Logan Road', 'Logan Central', 'QLD', 3, 1, FALSE, 'quiet', 'house', 'House1.jpg'),
(4, '18 Beachside Drive', 'Burleigh Heads', 'QLD', 5, 3, TRUE, 'social', 'house', 'House2.jpg'),
(3, '42 Garden Street', 'Ipswich', 'QLD', 4, 2, FALSE, 'social', 'house', 'House3.jpg'),
(4, '11 Mountain View Road', 'Toowoomba', 'QLD', 3, 2, TRUE, 'quiet', 'house', 'House1.jpg'),

-- Units
(3, '6 Station Lane', 'Indooroopilly', 'QLD', 2, 1, FALSE, 'social', 'unit', 'House2.jpg'),
(4, '90 Main Street', 'Chermside', 'QLD', 1, 1, TRUE, 'quiet', 'unit', 'House3.jpg'),
(3, '17 City View Court', 'Spring Hill', 'QLD', 2, 1, FALSE, 'social', 'unit', 'apartment.jpg'),

-- Granny Flats
(4, '3 Sunset Close', 'Caboolture', 'QLD', 1, 1, TRUE, 'quiet', 'granny_flat', 'grannyflathome.jpg'),
(3, '28 Lakeview Crescent', 'North Lakes', 'QLD', 1, 1, FALSE, 'social', 'granny_flat', 'grannyflathome.jpg');

INSERT INTO listings (property_id, title, description, weekly_price, availability_status)
VALUES
(1, 'CBD Apartment Queen Street', 'Modern city apartment', 520.00, 'available'),
(2, 'Adelaide Street Studio', 'Compact city living', 450.00, 'available'),
(3, 'Surfers Paradise Luxury Apartment', 'Beachside apartment', 780.00, 'available'),
(4, 'South Brisbane Riverside Apartment', 'Spacious river views', 650.00, 'available'),
(5, 'Eagle Street Apartment', 'Prime CBD location', 500.00, 'available'),

(6, 'Redcliffe Family Home', 'Large backyard home', 750.00, 'available'),
(7, 'Logan Central House', 'Affordable family home', 480.00, 'available'),
(8, 'Burleigh Beach House', 'Luxury beach house', 1200.00, 'available'),
(9, 'Ipswich Family House', 'Quiet suburban home', 600.00, 'available'),
(10, 'Toowoomba Home', 'Spacious rural home', 550.00, 'available'),

(11, 'Indooroopilly Unit', 'Near university', 420.00, 'available'),
(12, 'Chermside Unit', 'Modern unit', 400.00, 'available'),
(13, 'Spring Hill Unit', 'Central unit', 460.00, 'available'),

(14, 'Caboolture Granny Flat', 'Private living space', 300.00, 'available'),
(15, 'North Lakes Granny Flat', 'Quiet self-contained flat', 320.00, 'available');

INSERT INTO applications 
(seeker_id, listing_id, introduction_message, status, created_at)
VALUES
(6, 1, 'Interested in joining', 'pending', NOW()),
(5, 6, 'Would love to move in', 'accepted', NOW()),
(6, 8, 'Is this still available?', 'rejected', NOW());