#!/usr/bin/env bash
# Setup Qdrant (Docker) + Ollama (brew) + nomic-embed-text model.
#
# Usage: bash setup.sh
# Retreat: if this script takes > 4h end-to-end, abort (plan B2 retreat rule).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QDRANT_DATA="${SCRIPT_DIR}/qdrant-data"
QDRANT_CONTAINER="hermes-qdrant"
QDRANT_PORT="6333"
OLLAMA_MODEL="nomic-embed-text"

log() { printf '[setup] %s\n' "$*" >&2; }
fail() { printf '[setup] FAIL: %s\n' "$*" >&2; exit 1; }

# 1. Ollama
if ! command -v ollama >/dev/null 2>&1; then
    log "Ollama not found; installing via brew..."
    if ! command -v brew >/dev/null 2>&1; then
        fail "brew required. Install manually from https://ollama.com/download"
    fi
    brew install ollama || fail "brew install ollama failed"
fi
log "Ollama: $(ollama --version 2>&1 | head -1 || true)"

# Start ollama server in background if not running
if ! curl -fsS http://localhost:11434/api/tags >/dev/null 2>&1; then
    log "Starting ollama server..."
    ollama serve >"${SCRIPT_DIR}/ollama.log" 2>&1 &
    sleep 3
    curl -fsS http://localhost:11434/api/tags >/dev/null || fail "ollama server failed to start"
fi

# 2. Pull embedding model
if ! ollama list 2>/dev/null | grep -q "^${OLLAMA_MODEL}"; then
    log "Pulling ${OLLAMA_MODEL} (~270MB)..."
    ollama pull "${OLLAMA_MODEL}" || fail "ollama pull failed"
fi
log "Embedding model: ${OLLAMA_MODEL} ready"

# 3. Qdrant
if ! docker ps --format '{{.Names}}' | grep -q "^${QDRANT_CONTAINER}$"; then
    log "Starting Qdrant container..."
    mkdir -p "${QDRANT_DATA}"
    # Remove stopped container with same name
    docker rm -f "${QDRANT_CONTAINER}" >/dev/null 2>&1 || true
    docker run -d \
        --name "${QDRANT_CONTAINER}" \
        -p "${QDRANT_PORT}:6333" \
        -v "${QDRANT_DATA}:/qdrant/storage" \
        qdrant/qdrant:latest >/dev/null || fail "docker run qdrant failed"
    sleep 3
fi

# Healthcheck
if ! curl -fsS "http://localhost:${QDRANT_PORT}/collections" >/dev/null 2>&1; then
    fail "Qdrant healthcheck failed on port ${QDRANT_PORT}"
fi
log "Qdrant: http://localhost:${QDRANT_PORT} OK"

log "Setup complete. Next: python3 index.py && python3 eval.py"
