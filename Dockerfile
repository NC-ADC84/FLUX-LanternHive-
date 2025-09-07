# Multi-stage build for production deployment
FROM node:18-alpine AS frontend-builder

# Build frontend assets (if needed)
WORKDIR /app/frontend
COPY package*.json ./
RUN npm install

# Copy frontend files
COPY index.html style.css app.js ./

# Production Python backend
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_ENV=production

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy frontend files from builder stage
COPY --from=frontend-builder /app/frontend/index.html /app/
COPY --from=frontend-builder /app/frontend/style.css /app/
COPY --from=frontend-builder /app/frontend/app.js /app/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port (Cloud Run uses PORT environment variable)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Start the application
CMD ["python", "start_server.py"]
