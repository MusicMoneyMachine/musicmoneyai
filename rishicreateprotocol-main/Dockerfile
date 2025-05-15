# Build stage
FROM python:3.11-slim as builder
ARG DOCKER_CACHE_BUST=${DOCKER_CACHE_BUST}
ENV DOCKER_CACHE_BUST=${DOCKER_CACHE_BUST}

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock* /app/

# Project initialization:
# - Create a virtual environment in the /app/.venv directory
# - Install dependencies into the virtual environment
RUN poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-ansi --no-root

# Serving stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy project
COPY . /app

# Make sure the directory is in the Python path
ENV PYTHONPATH=/app

# Activate the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app/rishi_api

# Copy the entrypoint script into the container
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]