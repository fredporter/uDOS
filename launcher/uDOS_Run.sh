#!/bin/bash
# uDOS_Run.sh — Lightweight wrapper to boot uDOS from app bundle

cd "$(dirname "$0")/../" || exit 1
exec bash scripts/start.sh
