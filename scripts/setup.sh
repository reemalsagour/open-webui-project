#!/bin/bash

set -e

PROJECT_DIR="$HOME/open-webui-project/docker"

echo "======================================"
echo " AI Platform Setup"
echo "======================================"

echo ""
echo "[1] Updating system packages..."
sudo apt-get update

echo ""
echo "[2] Installing required packages..."
sudo apt-get install -y curl git ca-certificates postgresql-client

echo ""
echo "[3] Checking Docker..."

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker not found. Installing Docker Engine..."
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo usermod -aG docker "$USER"
    echo "Docker installed. You may need to log out and back in for group permissions to apply."
fi

echo ""
echo "[4] Starting Docker..."
sudo systemctl enable docker
sudo systemctl start docker

echo ""
echo "[5] Checking environment configuration..."
cd "$PROJECT_DIR"

if [ ! -f ../.env ]; then
    echo "ERROR: .env file not found at $HOME/open-webui-project/.env"
    exit 1
fi

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
echo "[6] Linking .env for Docker Compose..."
if [ ! -L .env ]; then
    ln -s ../.env .env
fi

echo ""
echo "[7] Starting services..."
docker compose up -d --build

echo ""
echo "[8] Deployment status..."
docker compose ps

echo ""
echo "======================================"
echo " Setup completed successfully"
echo " Provider: Google Gemini API"
echo " Database: Azure PostgreSQL Flexible Server"
echo "======================================"