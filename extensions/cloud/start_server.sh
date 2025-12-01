#!/bin/bash
# Start the POKE Online Flask server for dashboard and API
cd "$(dirname "$0")"
source ../../../.venv/bin/activate
python server.py
