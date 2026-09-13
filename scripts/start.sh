#!/bin/bash

set -e

PROJECT_DIR="$HOME/open-webui-project/docker"

echo "Starting Open WebUI and Ollama..."

cd "$PROJECT_DIR"

docker compose up -d

echo ""
echo "Services started."
docker compose ps