#!/bin/bash

set -e

PROJECT_DIR="$HOME/open-webui-project/docker"

echo "======================================"
echo " Project 10 - Starting Open WebUI"
echo "======================================"

cd "$PROJECT_DIR"

if [ ! -f .env ]; then
    echo "ERROR: .env file not found."
    echo "Please create $PROJECT_DIR/.env before starting."
    exit 1
fi

echo ""
echo "[1] Starting Docker Compose..."

docker compose up -d

echo ""
echo "[2] Container status..."

docker compose ps

echo ""
echo "======================================"
echo " Open WebUI started"
echo "======================================"
