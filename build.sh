#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
IMAGE="${ZMK_BUILD_IMAGE:-docker.io/zmkfirmware/zmk-build-arm:stable}"
PLATFORM="${ZMK_BUILD_PLATFORM:-linux/amd64}"
CACHE_VOLUME="${ZMK_BUILD_CACHE_VOLUME:-zmk-sofle-build-cache}"

if ! command -v docker >/dev/null 2>&1; then
    echo "error: Docker is required but was not found in PATH." >&2
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "error: Docker is installed, but its daemon is not running or is not accessible." >&2
    exit 1
fi

mkdir -p "${SCRIPT_DIR}/dist"
docker volume inspect "${CACHE_VOLUME}" >/dev/null 2>&1 || docker volume create "${CACHE_VOLUME}" >/dev/null

docker run --rm \
    --platform "${PLATFORM}" \
    --volume "${CACHE_VOLUME}:/workspace" \
    --volume "${SCRIPT_DIR}/config:/workspace/config:ro" \
    --volume "${SCRIPT_DIR}:/source:ro" \
    --volume "${SCRIPT_DIR}/dist:/dist" \
    --workdir /workspace \
    --env "HOST_UID=$(id -u)" \
    --env "HOST_GID=$(id -g)" \
    "${IMAGE}" \
    python3 /source/scripts/build_firmware.py "$@"
