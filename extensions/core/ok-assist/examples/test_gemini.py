#!/usr/bin/env python3
"""
Test Gemini API and list available models
"""

import os
import sys
from pathlib import Path

# Find project root (4 levels up from this file)
# examples/ -> ok-assist/ -> core/ -> extensions/ -> uDOS/
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent.parent.parent
env_file = project_root / '.env'

print(f"Current file: {current_file}")
print(f"Project root: {project_root}")
print(f"Looking for .env at: {env_file}")
print(f"Exists: {env_file.exists()}")

try:
    from dotenv import load_dotenv
    result = load_dotenv(env_file)
    print(f"✓ Loaded .env: {result}")
except ImportError:
    print("⚠ python-dotenv not installed, trying environment variables")
    pass

try:
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        sys.exit(1)

    print(f"✓ API Key found: {api_key[:20]}...")

    # Configure API
    genai.configure(api_key=api_key)

    # List available models
    print("\n📋 Available Gemini Models:")
    print("-" * 60)

    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✓ {model.name}")
            print(f"  Methods: {', '.join(model.supported_generation_methods)}")
            print()

    print("-" * 60)
    print("\n🧪 Testing model: gemini-2.5-flash")

    # Test generation
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Say 'Hello from Gemini!'")
        print(f"✅ Response: {response.text}")
        print("\n✅ Gemini API is working correctly!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Install: pip install google-generativeai python-dotenv")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
    traceback.print_exc()
    sys.exit(1)
