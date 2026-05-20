# --- STAGE 1: FRONTEND BUILD (Temporary helper stage) ---
FROM node:20-alpine AS frontend-builder
WORKDIR /build
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
# This generates the /build/dist folder
RUN npm run build

# --- TARGET: backend-stage ---
FROM python:3.11-slim AS backend-stage
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# --- TARGET: frontend-stage ---
FROM nginx:1.27-alpine AS frontend-stage
# Remove default nginx files
RUN rm -rf /usr/share/nginx/html/*
# Copy the BUILT static files from the builder stage
COPY --from=frontend-builder /build/dist /usr/share/nginx/html
# Copy your nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80