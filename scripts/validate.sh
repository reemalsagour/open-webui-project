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
echo "[4] Ollama models"
docker exec ollama ollama list

echo ""
echo "[5] Open WebUI health check"
curl -s http://localhost:3000/health

echo ""
echo ""
echo "======================================"
echo " Validation completed"
echo "======================================"