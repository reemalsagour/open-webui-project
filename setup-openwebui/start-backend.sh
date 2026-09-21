#!/bin/sh

set -e

API_KEY_FILE="/shared/openwebui_api_key"

echo "Waiting for Open WebUI API key..."

while [ ! -f "$API_KEY_FILE" ]; do
    sleep 1
done

echo "Open WebUI API key found."

export OPEN_WEB_UI_API_KEY="$(cat "$API_KEY_FILE")"

echo "Running database migrations..."
alembic upgrade head

echo "Checking database..."

USER_COUNT=$(python -c "from database import SessionLocal; from database_models import User; db=SessionLocal(); print(db.query(User).count()); db.close()")

if [ "$USER_COUNT" -eq "0" ]; then
    echo "Database is empty. Seeding database..."
    python seed.py
else
    echo "Database already contains data. Skipping seed."
fi

echo "Starting backend..."

exec "$@"