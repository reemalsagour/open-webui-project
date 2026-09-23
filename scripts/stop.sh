#!/bin/bash

set -e

PROJECT_DIR="$HOME/open-webui-project/docker"

echo "======================================"
echo " Stopping Open WebUI"
echo "======================================"

cd "$PROJECT_DIR"

echo ""
echo "[1] Stopping containers..."

docker compose stop

echo ""
echo "[2] Container status..."

docker compose ps

echo ""
echo "======================================"
echo " Open WebUI stopped"
echo "======================================"
