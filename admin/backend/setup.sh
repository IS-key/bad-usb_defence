#!/bin/bash

# Установка зависимостей для бэкенда
echo "Установка зависимостей для бэкенда..."
pip install flask flask-cors flask-sqlalchemy psycopg2-binary

# Создание директории для логов
mkdir -p logs

# Инициализация базы данных PostgreSQL
echo "Инициализация базы данных..."
sudo psql "postgresql://test:test@172.20.10.2:5432/test" -f init_db.sql

# Запуск Flask-приложения
echo "Запуск Flask-приложения..."
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
