#!/bin/bash

set -e

PROJECT_DIR="$HOME/open-webui-project/docker"

echo "======================================"
echo " AI Platform Setup"
echo "======================================"

echo ""
echo "[0] Checking Azure CLI..."
if ! command -v az >/dev/null 2>&1; then
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
fi

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
echo "[5] Pulling secrets from Azure Key Vault..."

VAULT_NAME="${1:-kv-openwebui-project}"
POSTGRES_HOST_ARG="${2:-}"
ADMIN_EMAIL_ARG="${3:-admin@yourcompany.com}"

az login --identity >/dev/null

POSTGRES_PASSWORD=$(az keyvault secret show --vault-name "$VAULT_NAME" --name postgres-password --query value -o tsv)
GEMINI_API_KEY=$(az keyvault secret show --vault-name "$VAULT_NAME" --name gemini-api-key --query value -o tsv)
JWT_SECRET_KEY=$(az keyvault secret show --vault-name "$VAULT_NAME" --name jwt-secret-key --query value -o tsv)
OPENWEBUI_ADMIN_PASSWORD=$(az keyvault secret show --vault-name "$VAULT_NAME" --name openwebui-admin-password --query value -o tsv)

cat > "$HOME/open-webui-project/.env" << EOF
POSTGRES_USER=openwebuiadmin
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_HOST=${POSTGRES_HOST_ARG:-psql-openwebui-project.postgres.database.azure.com}
POSTGRES_DB=openwebui
POSTGRES_SSL=require
GEMINI_API_KEY=${GEMINI_API_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
OPENWEBUI_ADMIN_EMAIL=${ADMIN_EMAIL_ARG}
OPENWEBUI_ADMIN_PASSWORD=${OPENWEBUI_ADMIN_PASSWORD}
FRONTEND_TEST_MODE=false
BACKEND_URL=http://backend:8000
EOF

cd "$PROJECT_DIR"
echo ".env file generated from Key Vault."

echo ""
echo "[6] Linking .env for Docker Compose..."
if [ ! -L .env ]; then
    ln -s ../.env .env
fi

echo ""
echo "[7] Starting services..."
sudo docker compose up -d --build

echo ""
echo "[8] Deployment status..."
sudo docker compose ps

echo ""
echo "======================================"
echo " Setup completed successfully"
echo " Provider: Google Gemini API"
echo " Database: Azure PostgreSQL Flexible Server"
echo "======================================"