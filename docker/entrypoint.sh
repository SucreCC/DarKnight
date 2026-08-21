#!/bin/sh
set -e

cd /app
mkdir -p /app/data/logs

echo "[docker] running database migrations..."
alembic upgrade head

echo "[docker] starting DarKnight..."
exec python -m darknight.main
