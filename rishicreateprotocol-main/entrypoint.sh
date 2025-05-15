#!/bin/bash
set -e

echo "Database is up - running migrations"
alembic upgrade head

echo "Starting Gunicorn"
exec gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000