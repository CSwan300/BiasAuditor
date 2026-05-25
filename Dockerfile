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

# Install system dependencies needed for C-extensions (like pandas/gcc) and healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install core build tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements and install globally
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Explicitly install uvicorn to ensure it's in the global site-packages
RUN pip install --no-cache-dir uvicorn

# Copy backend code into a subfolder to match the 'backend.main:app' module path
COPY backend/ ./backend/

# Environment setup
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
# Ensure the global python bin directory is in the PATH for the non-root user
ENV PATH="/usr/local/bin:${PATH}"

# Create non-root user and fix permissions for the /app directory
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Using 'python -m uvicorn' is the most robust way to start the app
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# --- STAGE 3: FRONTEND (Final Production Image) ---
FROM nginx:1.27-alpine AS frontend-stage

# Clean default nginx assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from Stage 1
COPY --from=frontend-builder /build/dist /usr/share/nginx/html

# Copy your custom nginx.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80