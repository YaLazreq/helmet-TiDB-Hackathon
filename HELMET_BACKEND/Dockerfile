# Utilise une image Python officielle comme base
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY .env .

EXPOSE 8000

CMD ["python", "backend.py"]