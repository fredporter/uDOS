#!/usr/bin/env python3
"""
uDOS - Universal Device Operating System
Main entry point: uCODE Unified Terminal TUI

uCODE is the pivotal single-entry-point Terminal TUI for uDOS that:
- Auto-detects available components (core, wizard, extensions)
- Gracefully falls back to core-only mode if other components are missing
- Handles extension/plugin packaging and distribution
- Controls Wizard server and exposes its pages
- Routes all core commands through the dispatcher
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Change to the workspace root for relative paths
os.chdir(project_root)

if __name__ == '__main__':
    from core.tui.ucode import uCODETUI
    tui = uCODETUI()
    tui.run()
