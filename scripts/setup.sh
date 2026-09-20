#!/bin/bash

set -e

PROJECT_DIR="$HOME/open-webui-project/docker"

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
echo "[5] Checking Gemini API configuration..."

cd "$PROJECT_DIR"

if [ ! -f .env ]; then
    echo "ERROR: .env file not found."
    echo "Create $PROJECT_DIR/.env with:"
    echo ""
    echo "GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE"
    echo ""
    exit 1
fi

if ! grep -q "^GEMINI_API_KEY=" .env; then
    echo "ERROR: GEMINI_API_KEY is missing from .env."
    exit 1
fi

echo ""
echo "[6] Starting Open WebUI..."

docker compose up -d

echo ""
echo "[7] Deployment status..."

docker compose ps

echo ""
echo "======================================"
echo " Setup completed successfully"
echo " Provider: Google Gemini API"
echo " Model: gemini-3.1-flash-lite"
echo "======================================"
