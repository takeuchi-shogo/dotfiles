#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DOTFILES_DIR="$(dirname "$(dirname "$PROJECT_DIR")")"
IMAGE_NAME="${IMAGE_NAME:-safeclaw-claude}"
SESSION_NAME="safeclaw"
MODEL=""
MOUNT_SCRIPTS=false

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        -s|--session)
            SESSION_NAME="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --mount-scripts)
            MOUNT_SCRIPTS=true
            shift
            ;;
        -h|--help)
            echo "Usage: run.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -s, --session NAME    Session name (default: safeclaw)"
            echo "  --model MODEL         Claude model to use"
            echo "  --mount-scripts       Mount scripts/ as read-write"
            echo "  -h, --help            Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

CONTAINER_NAME="${IMAGE_NAME}-${SESSION_NAME}"

# Docker availability check
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running." >&2
    exit 1
fi

# Image existence check
if ! docker image inspect "${IMAGE_NAME}" > /dev/null 2>&1; then
    echo "Error: Image '${IMAGE_NAME}' not found. Run build.sh first." >&2
    exit 1
fi

# API key check
if [ -z "${CLAUDE_API_KEY:-}" ]; then
    echo "Error: CLAUDE_API_KEY environment variable is not set." >&2
    exit 1
fi

# Build mount arguments
CLAUDE_CONFIG_DIR="${DOTFILES_DIR}/.config/claude"
MOUNT_ARGS=(
    -v "${CLAUDE_CONFIG_DIR}/CLAUDE.md:/home/claude/.claude/CLAUDE.md:ro"
    -v "${CLAUDE_CONFIG_DIR}/references:/home/claude/.claude/references:ro"
    -v "${CLAUDE_CONFIG_DIR}/skills:/home/claude/.claude/skills:ro"
    -v "${CLAUDE_CONFIG_DIR}/agents:/home/claude/.claude/agents:ro"
)

if [ "${MOUNT_SCRIPTS}" = true ]; then
    MOUNT_ARGS+=(-v "${CLAUDE_CONFIG_DIR}/scripts:/home/claude/.claude/scripts:rw")
    echo "Warning: scripts/ mounted as read-write"
fi

# Environment variables
ENV_ARGS=(
    -e "CLAUDE_API_KEY=${CLAUDE_API_KEY}"
)

if [ -n "${MODEL}" ]; then
    ENV_ARGS+=(-e "CLAUDE_MODEL=${MODEL}")
fi

echo "Starting session: ${SESSION_NAME}"
echo "Container: ${CONTAINER_NAME}"

docker run -it --rm \
    --name "${CONTAINER_NAME}" \
    "${MOUNT_ARGS[@]}" \
    "${ENV_ARGS[@]}" \
    "${IMAGE_NAME}"
