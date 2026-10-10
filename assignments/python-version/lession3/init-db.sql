-- Initialize sample database for agent testing

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER DEFAULT 0,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample users
INSERT INTO users (name, email, age) VALUES
    ('Alice Johnson', 'alice@example.com', 28),
    ('Bob Smith', 'bob@example.com', 35),
    ('Charlie Brown', 'charlie@example.com', 42),
    ('Diana Prince', 'diana@example.com', 31),
    ('Eve Anderson', 'eve@example.com', 26);

-- Insert sample products
INSERT INTO products (name, price, stock, category) VALUES
    ('Laptop Pro 15', 1299.99, 15, 'electronics'),
    ('Wireless Mouse', 29.99, 50, 'electronics'),
    ('Office Chair', 199.99, 8, 'furniture'),
    ('Standing Desk', 449.99, 5, 'furniture'),
    ('USB-C Cable', 12.99, 100, 'electronics'),
    ('Monitor 27"', 349.99, 20, 'electronics'),
    ('Keyboard Mechanical', 89.99, 30, 'electronics'),
    ('Desk Lamp', 39.99, 25, 'furniture'),
    ('Notebook Set', 15.99, 80, 'stationery'),
    ('Pen Pack', 5.99, 150, 'stationery');

-- Insert sample orders
INSERT INTO orders (user_id, total_amount, status) VALUES
    (1, 1329.98, 'completed'),
    (2, 199.99, 'completed'),
    (3, 799.97, 'pending'),
    (1, 349.99, 'shipped'),
    (4, 89.99, 'completed'),
    (5, 449.99, 'pending');

-- Create indexes for better query performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
