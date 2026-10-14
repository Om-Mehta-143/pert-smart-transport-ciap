# ==========================================
# Multi-Stage Dockerfile for PERT Web App
# Base: python:3.11-slim
# Security: Non-root execution, minimal layers
# ==========================================

# Stage 1: Build stage for dependency compilation
FROM python:3.11-slim AS builder

WORKDIR /app

# Prevent interactive prompts and Python bytecode caching
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Hardened Runtime Stage
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    PATH="/home/appuser/.local/bin:$PATH"

# Install curl for HEALTHCHECK only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root system user and group (UID/GID 10001)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

# Copy installed Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application files and enforce ownership
COPY --chown=appuser:appgroup app.py pert_engine.py ./
COPY --chown=appuser:appgroup templates/ ./templates/
COPY --chown=appuser:appgroup static/ ./static/

# Switch to non-root user
USER 10001:10001

EXPOSE 5000

# Health check probe against Flask /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Production WSGI server via gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "30", "app:app"]
