#!/bin/bash

set -e

PROJECT_DIR="$HOME/open-webui-project/docker"

echo "Stopping Open WebUI and Ollama..."

cd "$PROJECT_DIR"

docker compose stop

echo ""
echo "Services stopped."
docker compose ps