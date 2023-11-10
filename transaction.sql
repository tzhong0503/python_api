create database transaction_status;

use transaction_status;

select * from transactions;

select * from status;

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reference_number VARCHAR(255) UNIQUE,
    amount DECIMAL(10, 2),
    currency VARCHAR(3),
    description TEXT,
    payment_type VARCHAR(255),
    signature VARCHAR(255)
);

CREATE TABLE status (
    id INT AUTO_INCREMENT PRIMARY KEY,
     reference_number VARCHAR(255) UNIQUE,
     status VARCHAR(255)
     );
