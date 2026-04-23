CREATE DATABASE IF NOT EXISTS year_project;
USE year_project;

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    price DECIMAL(10, 2),
    stock INT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_date DATE,
    customer_id INT,
    payment_method VARCHAR(50),
    is_delivered BOOLEAN DEFAULT FALSE,
    total_price DECIMAL(10, 2),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    price DECIMAL(10, 2),
    amount INT,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO products (name, price, stock, is_active) VALUES
('Geurverspreider', 8.50, 15, True),
('Geurolie-eucalyptus', 8.50, 30, True),
('Geurolie-lavendel', 8.50, 30, True),
('Geurolie-vanille', 8.50, 30, True),
('Geurolie-cocosnoot', 8.50, 30, True),
('Geurolie-rose geranium', 8.50, 30, True),
('Geurolie-kaneel', 8.50, 30, True),
('Geurolie-jasmijn', 8.50, 30, True);

INSERT INTO customers (name, email, phone, is_active) VALUES
('Jan Janssen', 'jan.janssen@mail.com', '0470/12.34.56', True),
('Marie Peeters', 'marie.peeters@mail.com', '0471/23.45.67', True),
('Luc De Smet', 'luc.desmet@mail.com', '0472/34.56.78', True),
('Sofie Vermeulen', 'sofie.vermeulen@mail.com', '0473/45.67.89', True),
('Tom Claes', 'tom.claes@mail.com', '0474/56.78.90', True),
('Annelies Maes', 'annelies.maes@mail.com', '0475/67.89.01', True),
('Wim Jacobs', 'wim.jacobs@mail.com', '0476/78.90.12', True),
('Katrien Willems', 'katrien.willems@mail.com', '0477/89.01.23', True),
('Bart Mertens', 'bart.mertens@mail.com', '0478/90.12.34', True),
('Els Goossens', 'els.goossens@mail.com', '0479/01.23.45', True);

-- Note: Orders and Items below updated to use IDs assuming they match the insert order above (1, 2, 3)
INSERT INTO orders (id, order_date, customer_id, payment_method, is_delivered, total_price) VALUES
(1, '2026-04-20', 1, 'Payconic', TRUE, 25.50),
(2, '2026-04-21', 2, 'Cash', TRUE, 17.00),
(3, '2026-04-22', 3, 'Split', FALSE, 8.50);

INSERT INTO order_items (order_id, product_id, price, amount) VALUES
(1, 1, 8.50, 1),
(1, 2, 8.50, 2),
(2, 3, 8.50, 1),
(2, 4, 8.50, 1),
(3, 5, 8.50, 1);
