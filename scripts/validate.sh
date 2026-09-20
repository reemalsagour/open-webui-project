#!/bin/bash

set -e

PROJECT_DIR="$HOME/open-webui-project/docker"

echo "======================================"
echo " Project 10 - Platform Validation"
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
echo "[4] Gemini API configuration"

if [ -f .env ] && grep -q "^GEMINI_API_KEY=" .env; then
    echo "Gemini API key configuration found."
else
    echo "ERROR: Gemini API key configuration not found."
    exit 1
fi

echo ""
echo "[5] Open WebUI health check"
curl -s http://localhost:3000/health

echo ""
echo ""
echo "======================================"
echo " Validation completed"
echo " Provider: Google Gemini API"
echo "======================================"
