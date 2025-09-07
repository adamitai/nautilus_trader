# Nautilus Trader Arbitrage Tools - Production Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including nginx
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY arbitrage_tools/ ./arbitrage_tools/
COPY strategies/ ./strategies/

# Copy nginx configuration
COPY aws-infrastructure/docker/nginx.conf /etc/nginx/nginx.conf

# Copy frontend build (we'll build this separately)
COPY aws-infrastructure/docker/frontend/build/ ./frontend/build/

# Copy startup script
COPY aws-infrastructure/docker/start.sh ./start.sh

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app \
    && chmod +x /app/start.sh

# Switch to root for nginx and startup
USER root

# Create directories for data and nginx logs
RUN mkdir -p /app/data /app/logs /app/csv_output /var/log/nginx

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port 8000
EXPOSE 8000

# Default command - run backend API directly for now
CMD ["python", "arbitrage_tools/api_server.py"]