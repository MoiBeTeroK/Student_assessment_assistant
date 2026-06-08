FROM python:3.12-slim

# Настройка системных зависимостей для PostgreSQL и сборки пакетов
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    ffmpeg \
    libsndfile1 \
    sox \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копируем только список зависимостей
COPY requirements.txt .

# Установка библиотек
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код проекта из папки Backend
COPY . .

RUN mkdir -p /app/speech_to_text/model
RUN mkdir -p /app/speech_to_text/silero_vad

# Указываем порт, который будет слушать FastAPI
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]