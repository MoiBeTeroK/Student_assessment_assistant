FROM python:3.11.15-slim

# Настройка системных зависимостей для PostgreSQL и сборки пакетов
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копируем только список зависимостей
COPY requirements.txt .

# Установка библиотек
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код проекта из папки Backend
COPY . .

# Указываем порт, который будет слушать FastAPI
EXPOSE 8000

# Команда запуска сервера через gunicorn с использованием uvicorn-воркеров
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]