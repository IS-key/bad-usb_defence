-- Создание базы данных
CREATE DATABASE usb_control;

-- Подключение к базе данных
\c usb_control

-- Создание таблицы устройств
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    vid VARCHAR(10) NOT NULL,
    pid VARCHAR(10) NOT NULL,
    serial_number VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (vid, pid, serial_number)
);

-- Создание таблицы логов
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    device_name VARCHAR(100),
    vid VARCHAR(10),
    pid VARCHAR(10),
    serial_number VARCHAR(100),
    status VARCHAR(20),
    computer_name VARCHAR(100),
    ip_address VARCHAR(50),
    user_name VARCHAR(100)
);

-- Создание таблицы клиентов
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    computer_name VARCHAR(100) NOT NULL,
    ip_address VARCHAR(50) NOT NULL,
    user_name VARCHAR(100),
    os VARCHAR(50),
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'online',
    version VARCHAR(20),
    UNIQUE (computer_name, ip_address)
);

-- Добавление индексов для оптимизации запросов
CREATE INDEX idx_devices_vid_pid ON devices (vid, pid);
CREATE INDEX idx_logs_timestamp ON logs (timestamp);
CREATE INDEX idx_logs_status ON logs (status);
CREATE INDEX idx_clients_status ON clients (status);

-- Добавление тестовых данных
INSERT INTO devices (name, vid, pid, serial_number, description)
VALUES 
    ('Kingston USB Flash Drive', '0951', '1666', 'KB00000001', 'Корпоративная флешка'),
    ('Logitech USB Mouse', '046D', 'C52B', 'LG00000001', 'Офисная мышь'),
    ('Dell USB Keyboard', '413C', '2113', 'DL00000001', 'Стандартная клавиатура');
