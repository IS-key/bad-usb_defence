#!/bin/bash

# Запускаем бэкенд в фоновом режиме
cd /app/backend
python app.py &

# Запускаем фронтенд
cd /app
npm start
