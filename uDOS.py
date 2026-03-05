#!/usr/bin/env python3
"""uDOS root entrypoint shim.

Routes terminal launch to the v1.5 Bubble Tea interface via `bin/udos tui`.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Change to the workspace root for relative paths
os.chdir(project_root)
os.environ.setdefault("UDOS_ROOT", project_root)
os.environ.setdefault("UDOS_ROOT_REQUIRED", "1")

if __name__ == '__main__':
    launcher = os.path.join(project_root, "bin", "udos")
    if not os.path.exists(launcher):
        raise RuntimeError(f"uDOS launcher not found: {launcher}")
    os.execv(launcher, [launcher, "tui", *sys.argv[1:]])
