#!/bin/bash
set -e

echo "Starting Academic Management System (AMS) Docker Compose Stack..."
docker compose up -d

echo ""
echo "=================================================================="
echo "   🚀 Academic Management System (AMS) Stack is Up and Running!"
echo "=================================================================="
echo "   🔗 Services available on your host machine:"
echo "   • Frontend (Dev Mode)    : http://localhost:3000"
echo "   • Frontend (Nginx Prod)  : http://localhost:8080"
echo "   • Backend REST API       : http://localhost:8000"
echo "   • Swagger API Docs       : http://localhost:8000/docs"
echo "   • MinIO Admin Console    : http://localhost:9001"
echo "=================================================================="
echo ""
