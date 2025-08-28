#!/usr/bin/env python3
"""
uNETWORK Server API Test Client
Tests the uDOS server API endpoints for basic functionality
"""

import requests
import json
import time
import sys
from pathlib import Path

# Configuration
SERVER_URL = "http://127.0.0.1:8080"
TIMEOUT = 5

def test_endpoint(endpoint, description):
    """Test a single API endpoint"""
    print(f"Testing {description}...")
    try:
        response = requests.get(f"{SERVER_URL}{endpoint}", timeout=TIMEOUT)
        if response.status_code == 200:
            print(f"  ✅ {endpoint} - Status: {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
                print(f"  📄 Response keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
        else:
            print(f"  ❌ {endpoint} - Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ {endpoint} - Error: {e}")
    print()

def main():
    """Run API tests"""
    print("uDOS Server API Test Client")
    print("=" * 40)
    print(f"Server URL: {SERVER_URL}")
    print()

    # Check if server is running
    try:
        response = requests.get(SERVER_URL, timeout=TIMEOUT)
        print(f"✅ Server is running (Status: {response.status_code})")
    except requests.exceptions.RequestException:
        print(f"❌ Server is not accessible at {SERVER_URL}")
        print("Please start the server with: ./start-server.sh")
        return 1

    print()

    # Test common endpoints
    endpoints = [
        ("/api/status", "System status"),
        ("/api/system/info", "System information"),
        ("/api/system/health", "System health check"),
        ("/api/ucode/commands", "Available uCODE commands"),
        ("/api/memory/stats", "Memory statistics"),
    ]

    for endpoint, description in endpoints:
        test_endpoint(endpoint, description)

    print("API testing complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
