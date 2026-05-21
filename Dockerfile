# --- STAGE 1: FRONTEND BUILD ---
FROM node:20-alpine AS frontend-builder
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- STAGE 2: BACKEND ---
FROM python:3.11-slim AS backend-stage
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
gcc python3-dev curl && rm -rf /var/lib/apt/lists/* \

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run as non-root user for security
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# --- STAGE 3: FRONTEND ---
FROM nginx:1.27-alpine AS frontend-stage
RUN rm -rf /usr/share/nginx/html/*
COPY --from=frontend-builder /build/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80