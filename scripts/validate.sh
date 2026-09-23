#!/bin/bash

set -e

PROJECT_DIR="$HOME/open-webui-project/docker"

echo "======================================"
echo " Platform Validation"
echo "======================================"

cd "$PROJECT_DIR"

echo ""
echo "[1] Docker version"
docker --version

echo ""
echo "[2] Docker Compose version"
docker compose version

echo ""
echo "[3] Container status"
docker compose ps

echo ""
echo "[4] Environment configuration"
REQUIRED_VARS=(GEMINI_API_KEY POSTGRES_USER POSTGRES_PASSWORD POSTGRES_HOST POSTGRES_DB JWT_SECRET_KEY OPENWEBUI_ADMIN_EMAIL OPENWEBUI_ADMIN_PASSWORD)
MISSING=0
for VAR in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^${VAR}=.\+" ../.env; then
        echo "ERROR: $VAR is missing or empty in .env"
        MISSING=1
    fi
done
if [ "$MISSING" -eq 1 ]; then
    exit 1
fi
echo "All required environment variables are present."

echo ""
echo "[5] Open WebUI health check"
curl -sf http://localhost:3000/health && echo " -> OK" || echo " -> FAILED"

echo ""
echo "[6] Backend health check"
curl -sf http://localhost:8000/health && echo " -> OK" || echo " -> FAILED"

echo ""
echo "[7] Gemini connection check (via Open WebUI)"
docker compose exec -T open-webui env | grep -q "^OPENAI_API_KEYS=.\+" \
    && echo "Gemini API key is set inside the container." \
    || echo "WARNING: Gemini API key not found inside the container."

echo ""
echo "[8] Azure PostgreSQL connectivity check"
docker compose exec -T backend python -c "
from database import engine
try:
    with engine.connect():
        print('Database connection: OK')
except Exception as e:
    print('Database connection: FAILED -', e)
"

echo ""
echo "======================================"
echo " Validation completed"
echo " Provider: Google Gemini API"
echo " Database: Azure PostgreSQL Flexible Server"
echo "======================================"