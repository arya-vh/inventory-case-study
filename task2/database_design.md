-- Companies
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Warehouses
CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    name VARCHAR(255),
    location TEXT
);

-- Products
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    name VARCHAR(255),
    sku VARCHAR(100) UNIQUE,
    product_type VARCHAR(50), -- simple / bundle
    price DECIMAL(10,2)
);

-- Inventory (product in multiple warehouses)
CREATE TABLE inventory (
    product_id INT REFERENCES products(id),
    warehouse_id INT REFERENCES warehouses(id),
    quantity INT DEFAULT 0,
    PRIMARY KEY (product_id, warehouse_id)
);

-- Inventory history (tracking changes)
CREATE TABLE inventory_history (
    id SERIAL PRIMARY KEY,
    product_id INT,
    warehouse_id INT,
    quantity_changed INT,
    change_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Suppliers
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    contact_email VARCHAR(255)
);

-- Product-Supplier mapping
CREATE TABLE product_suppliers (
    product_id INT,
    supplier_id INT,
    PRIMARY KEY (product_id, supplier_id)
);

-- Bundles
CREATE TABLE product_bundles (
    bundle_product_id INT,
    component_product_id INT,
    quantity INT
);

-- Sales (for recent activity)
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    product_id INT,
    warehouse_id INT,
    quantity INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Low stock threshold
CREATE TABLE product_thresholds (
    product_id INT PRIMARY KEY,
    low_stock_threshold INT
);
