#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/core/grid-runtime"
NPM_CACHE_DIR="${NPM_CONFIG_CACHE:-$ROOT_DIR/.npm-cache}"

if [ ! -d "$RUNTIME_DIR" ]; then
  echo "Runtime directory not found: $RUNTIME_DIR"
  exit 1
fi

cd "$RUNTIME_DIR"
mkdir -p "$NPM_CACHE_DIR"
export NPM_CONFIG_CACHE="$NPM_CACHE_DIR"

if [ ! -d node_modules ]; then
  echo "Installing runtime dependencies..."
  npm install
fi

echo "Building TS runtime..."
npm run build
