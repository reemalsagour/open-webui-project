#!/bin/bash

set -e

PROJECT_DIR="$HOME/open-webui-project/docker"

echo "======================================"
echo " Starting Open WebUI"
echo "======================================"

cd "$PROJECT_DIR"

if [ ! -f ../.env ]; then
    echo "ERROR: .env file not found at $HOME/open-webui-project/.env"
    echo "Please create it before starting."
    exit 1
fi

if [ ! -L .env ]; then
    echo "Creating .env symlink for Docker Compose..."
    ln -s ../.env .env
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