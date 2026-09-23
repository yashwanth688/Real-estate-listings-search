-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS homefinder_db;
USE homefinder_db;

-- Drop existing tables to allow clean initialization (optional, careful in prod)
DROP TABLE IF EXISTS inquiries;
DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS properties;
DROP TABLE IF EXISTS users;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role ENUM('user', 'agent', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Properties table
CREATE TABLE properties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(12, 2) NOT NULL,
    location VARCHAR(150) NOT NULL,
    property_type ENUM('Apartment', 'House', 'Villa', 'Plot', 'Commercial') NOT NULL,
    status ENUM('Sale', 'Rent') NOT NULL,
    bedrooms INT DEFAULT 0,
    bathrooms INT DEFAULT 0,
    area INT NOT NULL COMMENT 'Area in sq ft',
    image_url VARCHAR(255) NOT NULL,
    amenities TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Favorites table (Many-to-Many between users and properties)
CREATE TABLE favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    property_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    UNIQUE(user_id, property_id)
);

-- Inquiries table (Contact form submissions for properties)
CREATE TABLE inquiries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(20),
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE SET NULL
);

-- Insert sample users
-- Note: password hashes are for the word 'password123' generated with Werkzeug generate_password_hash
INSERT INTO users (name, email, password_hash, phone, role) VALUES 
('Admin User', 'admin@homefinder.com', 'scrypt:32768:8:1$F8m72w6D2eZ2$1c54ef98539660c18b1d3d5267a57a553c3065d6bb4fc445ab028eb0a184e183789b9173f4586d11e8a4a5bb859747c3f3efdf09b52a12cf2c06941544a42b10', '123-456-7890', 'admin'),
('John Doe (Agent)', 'john@example.com', 'scrypt:32768:8:1$F8m72w6D2eZ2$1c54ef98539660c18b1d3d5267a57a553c3065d6bb4fc445ab028eb0a184e183789b9173f4586d11e8a4a5bb859747c3f3efdf09b52a12cf2c06941544a42b10', '555-0101', 'agent');

-- Insert sample properties
INSERT INTO properties (agent_id, title, description, price, location, property_type, status, bedrooms, bathrooms, area, image_url, amenities) VALUES 
(2, 'Modern Apartment in City Center', 'A beautiful, modern apartment located right in the heart of the city with stunning skyline views. Recently renovated with modern appliances.', 250000.00, 'Downtown, New York', 'Apartment', 'Sale', 2, 2, 1200, 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80', 'Gym, Swimming Pool, Parking'),
(2, 'Luxury Family Villa', 'Spacious family villa featuring a large backyard, private pool, and modern open-plan living area.', 850000.00, 'Beverly Hills, California', 'Villa', 'Sale', 5, 4, 4500, 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80', 'Pool, Garden, Garage, Security System'),
(2, 'Cozy Suburban House', 'Perfect starter home in a quiet suburban neighborhood. Close to great schools and parks.', 2000.00, 'Austin, Texas', 'House', 'Rent', 3, 2, 1800, 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80', 'Backyard, Garage, Pet Friendly');
