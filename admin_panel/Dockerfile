FROM python:3.12-slim

# Системные зависимости (только самое важное для БД и сборки)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код админки
COPY . .

# Порт внутри контейнера
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
