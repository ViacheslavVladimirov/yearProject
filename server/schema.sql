CREATE DATABASE IF NOT EXISTS year_project;
USE year_project;

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50) UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
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

    INSERT INTO products (name, price, stock) VALUES
    ('Geurverspreider', 8.50, 15),
    ('Geurolie-eucalyptus', 8.50, 30),
    ('Geurolie-lavendel', 8.50, 30),
    ('Geurolie-vanille', 8.50, 30),
    ('Geurolie-cocosnoot', 8.50, 30),
    ('Geurolie-rose geranium', 8.50, 30),
    ('Geurolie-kaneel', 8.50, 30),
    ('Geurolie-jasmijn', 8.50, 30);

    INSERT INTO customers (name, email, phone) VALUES
    ('Jan Janssen', 'jan.janssen@mail.com', '0470/12.34.56'),
    ('Marie Peeters', 'marie.peeters@mail.com', '0471/23.45.67'),
    ('Luc De Smet', 'luc.desmet@mail.com', '0472/34.56.78'),
    ('Sofie Vermeulen', 'sofie.vermeulen@mail.com', '0473/45.67.89'),
    ('Tom Claes', 'tom.claes@mail.com', '0474/56.78.90'),
    ('Annelies Maes', 'annelies.maes@mail.com', '0475/67.89.01'),
    ('Wim Jacobs', 'wim.jacobs@mail.com', '0476/78.90.12'),
    ('Katrien Willems', 'katrien.willems@mail.com', '0477/89.01.23'),
    ('Bart Mertens', 'bart.mertens@mail.com', '0478/90.12.34'),
    ('Els Goossens', 'els.goossens@mail.com', '0479/01.23.45');

    INSERT INTO orders (id, order_date, customer_name, payment_method, is_delivered, total_price) VALUES
    (1, '2026-04-20', 'Jan Janssen', 'Payconic', TRUE, 25.50),
    (2, '2026-04-21', 'Marie Peeters', 'Cash', TRUE, 17.00),
    (3, '2026-04-22', 'Luc De Smet', 'Split', FALSE, 8.50);

    INSERT INTO order_items (order_id, product_name, price, amount) VALUES
    (1, 'Geurverspreider', 8.50, 1),
    (1, 'Geurolie-eucalyptus', 8.50, 2),
    (2, 'Geurolie-lavendel', 8.50, 1),
    (2, 'Geurolie-vanille', 8.50, 1),
    (3, 'Geurolie-cocosnoot', 8.50, 1);