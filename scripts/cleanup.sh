#!/bin/bash

set -e

PROJECT_DIR="$HOME/open-webui-project/docker"

echo "======================================"
echo " Application Cleanup"
echo "======================================"

cd "$PROJECT_DIR"

echo ""
echo "Stopping and removing Open WebUI container..."

docker compose down

echo ""
echo "Application container removed."

echo ""
echo "Persistent Open WebUI Docker volume was NOT deleted."
echo "Your Open WebUI data remains preserved."

echo ""
echo "Gemini API configuration in .env was NOT deleted."

echo ""
echo "======================================"
echo " Cleanup completed"
echo "======================================"
