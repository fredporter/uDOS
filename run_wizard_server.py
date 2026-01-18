#!/usr/bin/env python
"""
Simple Wizard Server Launcher
================================
Starts the FastAPI server on port 8765 without TUI dependencies.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, '/Users/fredbook/Code/uDOS')

if __name__ == '__main__':
    import uvicorn

    try:
        print("🧙 Starting Wizard Server on http://127.0.0.1:8765")
        print("📊 Dashboard: http://127.0.0.1:8765/api/v1/config/dashboard")
        print("---")

        uvicorn.run(
            'public.wizard.server:app',
            host='127.0.0.1',
            port=8765,
            reload=False,
            log_level='info'
        )
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
