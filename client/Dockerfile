# Этап сборки фронтенда
FROM node:20 AS frontend-builder

WORKDIR /app

# Копируем только то, что нужно для сборки фронтенда
COPY frontend/package.json frontend/pnpm-lock.yaml ./frontend/
COPY package.json pnpm-lock.yaml ./

# Устанавливаем зависимости
RUN npm install -g pnpm
RUN pnpm install --frozen-lockfile

# Копируем остальные файлы фронтенда и собираем
COPY frontend ./frontend
COPY components ./components
COPY public ./public
COPY tailwind.config.ts postcss.config.mjs tsconfig.json next.config.mjs ./

RUN pnpm --filter frontend build

# Этап сборки бэкенда
FROM node:20 AS backend-builder

WORKDIR /app

# Копируем зависимости бэкенда
COPY backend/package.json backend/pnpm-lock.yaml ./backend/
COPY package.json pnpm-lock.yaml ./

# Устанавливаем зависимости
RUN npm install -g pnpm
RUN pnpm install --frozen-lockfile

# Копируем остальные файлы бэкенда
COPY backend ./backend
COPY lib ./lib

RUN pnpm --filter backend build

# Финальный образ
FROM node:20-alpine

WORKDIR /app

# Копируем зависимости
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm
RUN pnpm install --prod --frozen-lockfile

# Копируем собранные фронтенд и бэкенд
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/package.json ./frontend/
COPY --from=backend-builder /app/backend/dist ./backend/dist
COPY --from=backend-builder /app/backend/package.json ./backend/

# Устанавливаем зависимости для продакшена
RUN pnpm --filter frontend --prod --frozen-lockfile
RUN pnpm --filter backend --prod --frozen-lockfile

# Копируем скрипт для запуска
COPY setup.sh .

# Запускаем оба приложения
CMD ["sh", "-c", "pnpm --filter backend start & pnpm --filter frontend start"]
