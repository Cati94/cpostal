CREATE DATABASE postal_db;
USE postal_db;
CREATE TABLE postal_codes (
    postal_code VARCHAR(10) PRIMARY KEY,
    -- Example: '2520-193'"
    municipality VARCHAR(100),
    -- "Peniche"
    district VARCHAR(100),
    -- "Leiria"
);
postal_codes