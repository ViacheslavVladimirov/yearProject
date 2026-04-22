CREATE DATABASE IF NOT EXISTS year_project;
USE year_project;

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2),
    stock INT
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_date DATE,
    customer_name VARCHAR(255),
    payment_method VARCHAR(50),
    is_delivered BOOLEAN DEFAULT FALSE,
    total_price DECIMAL(10, 2)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_name VARCHAR(255),
    price DECIMAL(10, 2),
    amount INT,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
    );

    -- Seed Data
    INSERT INTO products (name, price, stock) VALUES
    ('Laptop', 1200.00, 15),
    ('Mouse', 25.00, 50),
    ('Keyboard', 45.00, 30),
    ('Monitor', 200.00, 20),
    ('Desk Chair', 150.00, 10),
    ('Desk Lamp', 35.00, 25),
    ('USB-C Cable', 15.00, 100),
    ('Webcam', 60.00, 15),
    ('Headset', 80.00, 12),
    ('External HDD', 90.00, 18);

    INSERT INTO customers (name, email, phone) VALUES
    ('Alice Johnson', 'alice.j@example.com', '555-0101'),
    ('Bob Smith', 'bob.s@example.com', '555-0102'),
    ('Charlie Brown', 'charlie.b@example.com', '555-0103'),
    ('Diana Prince', 'diana.p@example.com', '555-0104'),
    ('Edward Norton', 'edward.n@example.com', '555-0105'),
    ('Fiona Gallagher', 'fiona.g@example.com', '555-0106'),
    ('George Miller', 'george.m@example.com', '555-0107'),
    ('Hannah Abbott', 'hannah.a@example.com', '555-0108'),
    ('Ian Wright', 'ian.w@example.com', '555-0109'),
    ('Julia Roberts', 'julia.r@example.com', '555-0110');

    INSERT INTO orders (id, order_date, customer_name, payment_method, is_delivered, total_price) VALUES
    (1, '2026-03-01', 'Alice Johnson', 'Payconic', TRUE, 1225.00),
    (2, '2026-03-05', 'Bob Smith', 'Cash', TRUE, 245.00),
    (3, '2026-03-10', 'Charlie Brown', 'Payconic', TRUE, 185.00),
    (4, '2026-03-15', 'Diana Prince', 'Split', TRUE, 75.00),
    (5, '2026-03-20', 'Edward Norton', 'Payconic', FALSE, 170.00),
    (6, '2026-03-25', 'Fiona Gallagher', 'Cash', TRUE, 1200.00),
    (7, '2026-04-01', 'George Miller', 'Payconic', FALSE, 270.00),
    (8, '2026-04-05', 'Hannah Abbott', 'Split', TRUE, 50.00),
    (9, '2026-04-10', 'Ian Wright', 'Payconic', FALSE, 1280.00),
    (10, '2026-04-15', 'Julia Roberts', 'Cash', TRUE, 150.00);
    INSERT INTO order_items (order_id, product_name, price, amount) VALUES
    (1, 'Laptop', 1200.00, 1),
    (1, 'Mouse', 25.00, 1),
    (2, 'Monitor', 200.00, 1),
    (2, 'Keyboard', 45.00, 1),
    (3, 'Desk Chair', 150.00, 1),
    (3, 'Desk Lamp', 35.00, 1),
    (4, 'Webcam', 60.00, 1),
    (4, 'USB-C Cable', 15.00, 1),
    (5, 'Headset', 80.00, 1),
    (5, 'External HDD', 90.00, 1),
    (6, 'Laptop', 1200.00, 1),
    (7, 'Monitor', 200.00, 1),
    (7, 'Mouse', 25.00, 2),
    (7, 'Keyboard', 45.00, 1),
    (8, 'Desk Lamp', 35.00, 1),
    (8, 'USB-C Cable', 15.00, 1),
    (9, 'Laptop', 1200.00, 1),
    (9, 'Headset', 80.00, 1),
    (10, 'External HDD', 90.00, 1),
    (10, 'Webcam', 60.00, 1);
