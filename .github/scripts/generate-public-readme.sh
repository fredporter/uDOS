#!/bin/bash
# Generate public-facing README for uDOS-core mirror

cat > mirror/README.md << 'EOF'
# uDOS Core

Offline-first, distributed OS layer combining Python TUI, TypeScript runtime, and Tauri GUI.

This is the public distribution mirror of uDOS. For development and private components, see the private repository at fredporter/uDOS.

## What is Included

- core - TypeScript runtime for iOS, Android, and web
- wizard - AI routing and services
- extensions - API, transport, and VSCode support
- knowledge - Knowledge bank articles
- docs - Engineering documentation

## Installation

git clone https://github.com/fredporter/uDOS-core.git
cd uDOS-core
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

## Links

https://github.com/fredporter/uDOS-core
https://github.com/fredporter/uDOS

Automated mirror synced from the private repository.
EOF

echo "✅ Generated public README"
ls -lah mirror/README.md
