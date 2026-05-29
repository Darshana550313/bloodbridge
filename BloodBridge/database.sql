CREATE DATABASE IF NOT EXISTS bloodbridge CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bloodbridge;

DROP TABLE IF EXISTS donations;
DROP TABLE IF EXISTS blood_requests;
DROP TABLE IF EXISTS blood_inventory;
DROP TABLE IF EXISTS donors;
DROP TABLE IF EXISTS hospitals;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('donor', 'hospital', 'blood_bank', 'admin') NOT NULL DEFAULT 'donor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE donors (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    city VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    last_donation_date DATE NULL,
    eligibility_status ENUM('Eligible', 'Not Eligible') NOT NULL DEFAULT 'Eligible',
    CONSTRAINT fk_donors_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE hospitals (
    hospital_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL UNIQUE,
    hospital_name VARCHAR(160) NOT NULL,
    city VARCHAR(100) NOT NULL,
    contact VARCHAR(20) NOT NULL,
    CONSTRAINT fk_hospitals_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE blood_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    urgency ENUM('Low', 'Medium', 'High', 'Critical') NOT NULL,
    city VARCHAR(100) NOT NULL,
    request_status ENUM('Open', 'In Progress', 'Fulfilled', 'Cancelled') NOT NULL DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_requests_hospital FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id) ON DELETE CASCADE
);

CREATE TABLE blood_inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL UNIQUE,
    units_available INT NOT NULL DEFAULT 0 CHECK (units_available >= 0),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE donations (
    donation_id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    donation_date DATE NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    units INT NOT NULL CHECK (units > 0),
    CONSTRAINT fk_donations_donor FOREIGN KEY (donor_id) REFERENCES donors(donor_id) ON DELETE CASCADE
);

CREATE INDEX idx_donors_blood_city ON donors (blood_group, city);
CREATE INDEX idx_requests_blood_city_status ON blood_requests (blood_group, city, request_status);
CREATE INDEX idx_inventory_group ON blood_inventory (blood_group);

INSERT INTO users (id, name, email, password, role) VALUES
(1, 'Admin User', 'admin@bloodbridge.local', 'scrypt:32768:8:1$TGDweyz08B60G0NX$d56773ca173c339f44960274e5435b581e0e8be5861e1c65675ea76d11fb0f22e7303f5e8b047cc9435916a3b98481cbe6f6cf5be32e68848bc649f2454b2715', 'admin'),
(2, 'Asha Donor', 'donor@bloodbridge.local', 'scrypt:32768:8:1$2PSr4l2ndN26agCv$5bb2423c4b3482747bb74bb728673eace0ab6f9e2314940e8c3b9f41599b0f8cf672c15e507e7aabfce03f22e969015bbcda098fcbf020f231a00a2b35479749', 'donor'),
(3, 'CityCare Hospital', 'hospital@bloodbridge.local', 'scrypt:32768:8:1$Il7Wcg3SDtfOFnc7$d28d2e1dfb0ab05a060ca3f66f196a6e20d6a7700b06815802d7392ffa5c4bd5c409433806c11e583d3ecabb2ac93cd7c9c4e41493eb29e1307cbe59f99c2460', 'hospital'),
(4, 'Central Blood Bank', 'bank@bloodbridge.local', 'scrypt:32768:8:1$SvYziSNhRhAA0cQb$1b92a0aefb526210172bfb9ced75af9fb252c962e666bd50df4c328092c100e848f3b574841a6c267d7c6dd22e83b6cd0a9ed436e20d8d2a65230508244afa24', 'blood_bank');

INSERT INTO donors (donor_id, user_id, blood_group, city, phone, last_donation_date, eligibility_status) VALUES
(1, 2, 'O+', 'Pune', '+91 9876543210', '2026-01-10', 'Eligible');

INSERT INTO hospitals (hospital_id, user_id, hospital_name, city, contact) VALUES
(1, 3, 'CityCare Hospital', 'Pune', '+91 9123456780');

INSERT INTO blood_inventory (blood_group, units_available) VALUES
('A+', 26), ('A-', 9), ('B+', 18), ('B-', 7), ('AB+', 12), ('AB-', 5), ('O+', 31), ('O-', 8);

INSERT INTO blood_requests (hospital_id, blood_group, quantity, urgency, city, request_status) VALUES
(1, 'O+', 3, 'Critical', 'Pune', 'Open'),
(1, 'A-', 2, 'High', 'Pune', 'In Progress');

INSERT INTO donations (donor_id, donation_date, blood_group, units) VALUES
(1, '2026-01-10', 'O+', 1);

