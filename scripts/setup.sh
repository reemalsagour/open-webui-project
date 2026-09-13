#!/bin/bash

set -e

PROJECT_DIR="$HOME/open-webui-project/docker"
MODEL="llama3.2:3b"

echo "======================================"
echo " Project 10 - AI Platform Setup"
echo "======================================"

echo ""
echo "[1] Updating system packages..."

sudo apt-get update

echo ""
echo "[2] Installing required packages..."

sudo apt-get install -y curl git

echo ""
echo "[3] Checking Docker..."

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is not installed."
    echo "Please install Docker before running this script."
    exit 1
fi

echo ""
echo "[4] Starting Docker..."

sudo systemctl enable docker
sudo systemctl start docker

echo ""
echo "[5] Starting application..."

cd "$PROJECT_DIR"

docker compose up -d

echo ""
echo "[6] Waiting for Ollama..."

sleep 10

echo ""
echo "[7] Downloading AI model..."

docker exec ollama ollama pull "$MODEL"

echo ""
echo "[8] Deployment status..."

docker compose ps

echo ""
echo "======================================"
echo " Setup completed successfully"
echo " Model: $MODEL"
echo "======================================"