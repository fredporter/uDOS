#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_SRC="$APP_ROOT/src"

if [ ! -d "$APP_SRC" ]; then
  echo "App source submodule missing at $APP_SRC"
  echo "Run: cd app && git submodule update --init --recursive"
  exit 1
fi

cd "$APP_SRC"

if [ ! -d node_modules ]; then
  echo "Installing dependencies..."
  npm install
fi

echo "Building Tauri app..."
npm run tauri:build
