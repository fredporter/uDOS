#!/usr/bin/env bash
set -euo pipefail

find . \
  -path './.venv' -prune -o \
  -path './venv' -prune -o \
  -path './node_modules' -prune -o \
  -path './web-admin/node_modules' -prune -o \
  -path './wizard/dashboard/node_modules' -prune -o \
  -type d -name '__pycache__' -print -exec rm -rf {} +

rm -rf .pytest_cache .artifacts-pytest-tmp
