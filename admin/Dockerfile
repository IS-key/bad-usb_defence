# Используем образ с поддержкой Node.js и Python
FROM nikolaik/python-nodejs:python3.9-nodejs18

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей для бэкенда
COPY backend/requirements.txt ./backend/

# Устанавливаем зависимости для бэкенда
RUN pip install --no-cache-dir -r backend/requirements.txt

# Копируем файлы зависимостей для фронтенда
COPY package.json package-lock.json* ./

# Устанавливаем зависимости для фронтенда
RUN npm ci

# Копируем исходный код
COPY . .

# Собираем фронтенд
RUN npm run build

# Создаем файл запуска для обоих сервисов
COPY start.sh ./
RUN chmod +x start.sh

# Открываем порты
EXPOSE 3000 5000

# Запускаем оба сервиса
CMD ["./start.sh"]
