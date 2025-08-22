#!/usr/bin/env python3
"""
uDOS CLI Server (Ghost/Tomb roles)
Runs Bash/uCODE scripts, outputs to CLI only.
"""
import subprocess
import sys
import os

def run_ucode_script(script_path, args=None):
    if not os.path.isfile(script_path):
        print(f"ERROR: Script not found: {script_path}")
        sys.exit(1)
    cmd = [script_path] + (args if args else [])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Script error: {e.stderr}")
        sys.exit(e.returncode)

def main():
    if len(sys.argv) < 2:
        print("Usage: cli_server.py <script> [args...]")
        sys.exit(1)
    script = sys.argv[1]
    args = sys.argv[2:]
    run_ucode_script(script, args)

if __name__ == "__main__":
    main()
