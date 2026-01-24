#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/core/grid-runtime"

if [ ! -d "$RUNTIME_DIR" ]; then
  echo "Runtime directory not found: $RUNTIME_DIR"
  exit 1
fi

cd "$RUNTIME_DIR"

if [ ! -d node_modules ]; then
  echo "Installing runtime dependencies..."
  npm install
fi

echo "Building TS runtime..."
npm run build
