#!/bin/bash

set -e

PROJECT_DIR="$HOME/open-webui-project/docker"

echo "======================================"
echo " Project 10 - Application Cleanup"
echo "======================================"

cd "$PROJECT_DIR"

echo ""
echo "Stopping and removing containers..."

docker compose down

echo ""
echo "Application containers removed."

echo ""
echo "Persistent Docker volumes were NOT deleted."
echo "Your Open WebUI data and Ollama model remain preserved."

echo ""
echo "======================================"
echo " Cleanup completed"
echo "======================================"