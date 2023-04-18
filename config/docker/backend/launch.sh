#!/usr/bin/env bash

echo "Applying alembic migrations"
alembic upgrade head || exit 1

echo "Starting API"
uvicorn app.main:app --host "0.0.0.0" --port 8000 --proxy-headers --no-server-header
