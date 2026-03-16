#!/bin/bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-safeclaw-claude}"
SESSION_NAME=""
STOP_ALL=false

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        -s|--session)
            SESSION_NAME="$2"
            shift 2
            ;;
        --all)
            STOP_ALL=true
            shift
            ;;
        -h|--help)
            echo "Usage: stop.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -s, --session NAME    Stop specific session (default: safeclaw)"
            echo "  --all                 Stop all safeclaw sessions"
            echo "  -h, --help            Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

if [ "${STOP_ALL}" = true ]; then
    echo "Stopping all ${IMAGE_NAME} containers..."
    containers=$(docker ps -q --filter "name=${IMAGE_NAME}-" 2>/dev/null || true)
    if [ -z "${containers}" ]; then
        echo "No running containers found."
        exit 0
    fi
    echo "${containers}" | xargs docker stop
    echo "Done."
else
    CONTAINER_NAME="${IMAGE_NAME}-${SESSION_NAME:-safeclaw}"
    echo "Stopping container: ${CONTAINER_NAME}"
    if docker stop "${CONTAINER_NAME}" 2>/dev/null; then
        echo "Done."
    else
        echo "Container '${CONTAINER_NAME}' is not running."
    fi
fi
