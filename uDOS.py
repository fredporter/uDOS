#!/usr/bin/env python3
"""
uDOS - Universal Device Operating System
Main entry point (imports from dev/goblin/core/)
"""

import sys
import os

# Add the dev/goblin directory to the path so we can import core as a package
dev_dir = os.path.join(os.path.dirname(__file__), 'dev', 'goblin')
sys.path.insert(0, dev_dir)

# Change to the workspace root for relative paths used in uDOS
os.chdir(os.path.dirname(__file__))

if __name__ == '__main__':
    from core.uDOS_main import main
    main()
