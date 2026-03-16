#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="${IMAGE_NAME:-safeclaw-claude}"

echo "Building ${IMAGE_NAME}..."
docker build -t "${IMAGE_NAME}" "${PROJECT_DIR}"
echo "Done. Image: ${IMAGE_NAME}"
