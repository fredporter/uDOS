#!/usr/bin/env python3
"""
uDOS - Universal Device Operating System
Main entry point for the new lightweight TUI
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Change to the workspace root for relative paths
os.chdir(project_root)

if __name__ == '__main__':
    from core.tui.repl import TUIRepl
    repl = TUIRepl()
    repl.run()
