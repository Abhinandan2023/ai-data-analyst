INSERT INTO customers (name, email, city) VALUES
('Rahul Sharma', 'rahul@example.com', 'Delhi'),
('Priya Mehta', 'priya@example.com', 'Mumbai'),
('Arjun Singh', 'arjun@example.com', 'Bangalore'),
('Sneha Das', 'sneha@example.com', 'Kolkata'),
('Vikram Patel', 'vikram@example.com', 'Ahmedabad');

INSERT INTO products (name, category, price) VALUES
('Laptop Pro 15', 'Electronics', 85000),
('Wireless Headphones', 'Electronics', 12000),
('Mechanical Keyboard', 'Accessories', 7500),
('4K Monitor', 'Electronics', 32000),
('Wireless Mouse', 'Accessories', 2500),
('USB-C Hub', 'Accessories', 4500);

INSERT INTO orders (customer_id, order_date, status) VALUES
(1, '2026-08-01', 'completed'),
(1, '2026-08-15', 'completed'),
(1, '2026-09-05', 'completed'),
(2, '2026-08-10', 'completed'),
(2, '2026-09-12', 'completed'),
(3, '2026-08-20', 'completed'),
(4, '2026-09-01', 'completed'),
(4, '2026-09-18', 'completed'),
(5, '2026-09-20', 'completed');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 85000),
(1, 2, 1, 12000),
(2, 4, 1, 32000),
(2, 5, 2, 2500),
(3, 1, 1, 85000),
(4, 4, 1, 32000),
(4, 3, 1, 7500),
(5, 2, 2, 12000),
(6, 1, 1, 85000),
(6, 6, 1, 4500),
(7, 3, 2, 7500),
(7, 5, 2, 2500),
(8, 4, 1, 32000),
(9, 2, 1, 12000),
(9, 6, 1, 4500);