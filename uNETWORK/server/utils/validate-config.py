#!/usr/bin/env python3
"""
uNETWORK Server Configuration Validator
Validates server configuration files and environment
"""

import json
import sys
import os
from pathlib import Path

def validate_config_file(config_path):
    """Validate a JSON configuration file"""
    print(f"Validating {config_path}...")

    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return False

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"✅ Valid JSON structure")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False

    # Validate required sections
    required_sections = ['server', 'security', 'logging', 'paths', 'features']
    missing_sections = []

    for section in required_sections:
        if section not in config:
            missing_sections.append(section)

    if missing_sections:
        print(f"❌ Missing required sections: {missing_sections}")
        return False
    else:
        print(f"✅ All required sections present")

    # Validate server section
    server_config = config.get('server', {})
    required_server_fields = ['host', 'port']

    for field in required_server_fields:
        if field not in server_config:
            print(f"❌ Missing server.{field}")
            return False

    # Validate port number
    port = server_config.get('port')
    if not isinstance(port, int) or port < 1 or port > 65535:
        print(f"❌ Invalid port number: {port}")
        return False

    print(f"✅ Server configuration valid (host: {server_config['host']}, port: {port})")

    # Validate paths
    paths_config = config.get('paths', {})
    base_dir = Path(__file__).parent.parent.parent.parent  # uDOS root

    for path_name, path_value in paths_config.items():
        if path_name == 'udos_root':
            continue

        full_path = base_dir / path_value
        if not full_path.exists():
            print(f"⚠️ Path not found: {path_name} -> {full_path}")
        else:
            print(f"✅ Path valid: {path_name}")

    return True

def check_python_dependencies():
    """Check if required Python packages are available"""
    print("\nChecking Python dependencies...")

    required_packages = [
        'flask',
        'flask_socketio',
        'eventlet',
        'requests'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('_', '.') if '_' in package else package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n❌ Missing packages: {missing_packages}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    else:
        print("✅ All required packages available")
        return True

def check_environment():
    """Check environment variables and system setup"""
    print("\nChecking environment...")

    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 7):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python version too old: {python_version.major}.{python_version.minor}")
        return False

    # Check for uSCRIPT virtual environment
    udos_root = Path(__file__).parent.parent.parent.parent
    venv_path = udos_root / "uSCRIPT" / "venv" / "python"

    if venv_path.exists():
        print(f"✅ uSCRIPT virtual environment found")
    else:
        print(f"⚠️ uSCRIPT virtual environment not found")
        print(f"   Run: cd {udos_root}/uSCRIPT && ./setup-environment.sh")

    # Check port availability
    import socket
    port = 8080
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(('127.0.0.1', port))
        if result == 0:
            print(f"⚠️ Port {port} is already in use")
        else:
            print(f"✅ Port {port} is available")

    return True

def main():
    """Run all validation checks"""
    print("uNETWORK Server Configuration Validator")
    print("=" * 45)

    # Find config file
    config_dir = Path(__file__).parent.parent / "config"
    config_files = list(config_dir.glob("*.json"))

    if not config_files:
        print("❌ No configuration files found in config/ directory")
        return 1

    # Validate each config file
    all_valid = True
    for config_file in config_files:
        if not validate_config_file(config_file):
            all_valid = False
        print()

    # Check dependencies
    if not check_python_dependencies():
        all_valid = False

    # Check environment
    if not check_environment():
        all_valid = False

    print("\n" + "=" * 45)
    if all_valid:
        print("✅ All checks passed - server should start successfully")
        return 0
    else:
        print("❌ Some checks failed - please fix issues before starting server")
        return 1

if __name__ == "__main__":
    sys.exit(main())
