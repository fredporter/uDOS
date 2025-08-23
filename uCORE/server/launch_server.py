#!/usr/bin/env python3
"""
uDOS Role-Detection Launcher
Detects user role from uMEMORY/user/installation.md and launches appropriate server.
"""
import os
import sys
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
INSTALL_MD = os.path.join(ROOT_DIR, 'uMEMORY/user/installation.md')
CLI_SERVER = os.path.join(ROOT_DIR, 'uCORE/server/cli_server.py')
UI_SERVER = os.path.join(ROOT_DIR, 'uNETWORK/server/ui_server.py')

# Parse role from installation.md
ROLE = None
if os.path.isfile(INSTALL_MD):
    with open(INSTALL_MD, 'r') as f:
        for line in f:
            if line.lower().startswith('role:'):
                ROLE = line.split(':', 1)[1].strip().lower()
                break
else:
    print(f"ERROR: {INSTALL_MD} not found.")
    sys.exit(1)

if not ROLE:
    print("ERROR: Role not found in installation.md.")
    sys.exit(1)

print(f"Detected role: {ROLE}")

if ROLE in ['ghost', 'tomb']:
    print("Launching CLI server for Ghost/Tomb...")
    subprocess.run(['python3', CLI_SERVER] + sys.argv[1:])
elif ROLE in ['crypt', 'knight', 'imp', 'sorcerer', 'wizard']:
    print("Launching UI server for Crypt+...")
    subprocess.run(['python3', UI_SERVER])
else:
    print(f"ERROR: Unknown role '{ROLE}'.")
    sys.exit(1)
