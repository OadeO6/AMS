#!/usr/bin/env bash
# backend/scripts/create_minio_bucket.sh
#
# One-time script to create the MinIO bucket and set it to public-read.
# Run this against a live MinIO instance whenever you need to re-initialise
# storage (fresh environment, CI, etc.).
#
# Usage:
#   MINIO_ENDPOINT=http://localhost:9000 \
#   MINIO_USER=ams_minio_user            \
#   MINIO_PASS=ams_minio_pass            \
#   MINIO_BUCKET=ams-storage-bucket      \
#   bash backend/scripts/create_minio_bucket.sh
#
# Defaults match the docker-compose.yml values so you can run it with no args
# in a standard local dev setup.
#
# Requires: minio/mc (MinIO Client) to be installed.
#   Docker:  docker run --rm --network host minio/mc ...
#   Brew:    brew install minio/stable/mc
#   Direct:  https://dl.min.io/client/mc/release/linux-amd64/mc

set -euo pipefail

MINIO_ENDPOINT="${MINIO_ENDPOINT:-http://localhost:9000}"
MINIO_USER="${MINIO_USER:-ams_minio_user}"
MINIO_PASS="${MINIO_PASS:-ams_minio_pass}"
MINIO_BUCKET="${MINIO_BUCKET:-ams-storage-bucket}"
ALIAS="ams-local"

echo "→ Configuring MinIO alias '${ALIAS}' → ${MINIO_ENDPOINT}"
mc alias set "${ALIAS}" "${MINIO_ENDPOINT}" "${MINIO_USER}" "${MINIO_PASS}"

echo "→ Creating bucket '${MINIO_BUCKET}' (no-op if already exists)"
mc mb --ignore-existing "${ALIAS}/${MINIO_BUCKET}"

echo "→ Setting bucket to public-read"
# mc anonymous replaces the deprecated 'mc policy set' command
mc anonymous set public "${ALIAS}/${MINIO_BUCKET}"

echo "✓ Bucket '${MINIO_BUCKET}' is ready on ${MINIO_ENDPOINT}"
