#!/usr/bin/env python3
"""
Quick test of DIAGRAM GENERATE command
"""

import os
import sys
from pathlib import Path

# Set up path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"\'')

print("✅ Environment loaded")
print(f"   API Key: {os.getenv('GEMINI_API_KEY', 'NOT FOUND')[:15]}...")
print()

# Import and test
from core.commands.diagram_handler import DiagramHandler

handler = DiagramHandler()
print("🧪 Testing DIAGRAM GENERATE...")
print()

result = handler.handle('GENERATE', ['sandbox/test_water_purification.md'])
print(result)
