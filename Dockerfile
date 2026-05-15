# --- STAGE 1: BACKEND ---
FROM python:3.11-slim AS backend-stage
WORKDIR /app

# Copy requirements from the root and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend folder into /app/backend
COPY backend/ ./backend/

EXPOSE 8000

# Tell Python to look in the /app folder for packages
ENV PYTHONPATH=/app

# Run uvicorn pointing to the file inside the backend folder
# Format: folder.filename:variable
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# --- STAGE 2: FRONTEND ---
FROM nginx:1.27-alpine AS frontend-stage
RUN rm -rf /usr/share/nginx/html/*
COPY frontend/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80