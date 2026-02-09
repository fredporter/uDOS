#!/bin/bash
# Start Wizard Server Web Interface

# Activate venv
source venv/bin/activate

# Install dependencies if needed
pip install fastapi uvicorn python-multipart jinja2 qrcode 2>/dev/null

# Start server
echo "🧙 Starting Wizard Server Web Interface..."
echo "📍 Dashboard: http://127.0.0.1:8080/"
echo ""
python -c "from wizard.web.app import start_web_server; start_web_server()"
