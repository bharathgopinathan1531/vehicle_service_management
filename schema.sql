CREATE DATABASE vehicle_service_db;

USE vehicle_service_db;

CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE vehicles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    vehicle_number VARCHAR(50) UNIQUE NOT NULL,
    brand VARCHAR(50),
    model VARCHAR(50),
    customer_id INT,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE service_requests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    vehicle_id INT,
    service_type VARCHAR(100),
    service_cost DECIMAL(10,2) CHECK (service_cost > 0),
    service_date DATE,
    status ENUM('Pending','In Progress','Completed') DEFAULT 'Pending',
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);

-- Sample Data

INSERT INTO customers(name, phone, email)
VALUES
('Bharath','9876543210','bharath@gmail.com'),
('Rahul','9876543211','rahul@gmail.com');

INSERT INTO vehicles(vehicle_number, brand, model, customer_id)
VALUES
('KA01AB1234','Honda','City',1),
('KA02CD5678','Hyundai','i20',1),
('KA03EF9999','Toyota','Innova',2);

INSERT INTO service_requests(vehicle_id, service_type, service_cost, service_date, status)
VALUES
(1,'Oil Change',2000,'2025-06-01','Completed'),
(1,'Wheel Alignment',1500,'2025-06-02','Pending'),
(2,'Engine Service',5000,'2025-06-03','Completed'),
(3,'General Service',3000,'2025-06-04','In Progress');

-- LEVEL 5 SQL TASKS

-- 1. Customers with multiple vehicles
SELECT c.id, c.name, COUNT(v.id) AS vehicle_count
FROM customers c
JOIN vehicles v ON c.id = v.customer_id
GROUP BY c.id, c.name
HAVING COUNT(v.id) > 1;

-- 2. Total service revenue
SELECT SUM(service_cost) AS total_revenue
FROM service_requests;

-- 3. Vehicles with highest number of services
SELECT vehicle_id, COUNT(*) AS total_services
FROM service_requests
GROUP BY vehicle_id
ORDER BY total_services DESC;

-- 4. Monthly service report
SELECT
YEAR(service_date) AS year,
MONTH(service_date) AS month,
COUNT(*) AS total_services,
SUM(service_cost) AS revenue
FROM service_requests
GROUP BY YEAR(service_date), MONTH(service_date);

-- 5. Pending service requests
SELECT *
FROM service_requests
WHERE status = 'Pending';

-- 6. Rank customers by total spending
SELECT
c.id,
c.name,
SUM(sr.service_cost) AS total_spending,
RANK() OVER (ORDER BY SUM(sr.service_cost) DESC) AS ranking
FROM customers c
JOIN vehicles v ON c.id = v.customer_id
JOIN service_requests sr ON v.id = sr.vehicle_id
GROUP BY c.id, c.name;