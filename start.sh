#!/bin/bash
set -e

# Load configurations if .env files exist
if [ -f backend/.env ]; then
  # Export backend env, but don't overwrite existing environment variables
  while IFS= read -r line || [ -n "$line" ]; do
    if [[ ! "$line" =~ ^# ]] && [[ "$line" =~ = ]]; then
      key=$(echo "$line" | cut -d'=' -f1)
      val=$(echo "$line" | cut -d'=' -f2-)
      # Remove surrounding quotes if any
      val="${val%\"}"
      val="${val#\"}"
      val="${val%\'}"
      val="${val#\'}"
      if [ -z "${!key}" ]; then
        export "$key=$val"
      fi
    fi
  done < backend/.env
fi

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Define port defaults
API_PORT=${API_PORT:-8000}
FRONTEND_DEV_PORT=${FRONTEND_DEV_PORT:-3000}
FRONTEND_PROD_PORT=${FRONTEND_PROD_PORT:-8080}
MINIO_PORT=${MINIO_PORT:-9001}
TEST_PAGES_PORT=${TEST_PAGES_PORT:-8081}

echo "Starting Academic Management System (AMS) Docker Compose Stack..."
docker compose up -d

echo ""
echo "=================================================================="
echo "   🚀 Academic Management System (AMS) Stack is Up and Running!"
echo "=================================================================="
echo "   🔗 Services available on your host machine:"
echo "   • Frontend (Dev Mode)    : http://localhost:${FRONTEND_DEV_PORT}"
echo "   • Frontend (Nginx Prod)  : http://localhost:${FRONTEND_PROD_PORT}"
echo "   • Backend REST API       : http://localhost:${API_PORT}"
echo "   • Swagger API Docs       : http://localhost:${API_PORT}/docs"
echo "   • MinIO Admin Console    : http://localhost:${MINIO_PORT}"
echo "   • Static Test Pages      : http://localhost:${TEST_PAGES_PORT}"
echo "=================================================================="
echo ""

