#!/usr/bin/env python3
"""Direct test of RESTORE command handler"""

import sys
sys.path.insert(0, '/Users/fredbook/Code/uDOS')

from core.uDOS_commands import CommandHandler
from core.uDOS_grid import Grid
from core.uDOS_parser import Parser
from core.uDOS_logger import Logger
from core.services.history_manager import ActionHistory

# Initialize components
parser = Parser()
grid = Grid()
logger = Logger()
history = ActionHistory(logger=logger)

# Initialize command handler
command_handler = CommandHandler(history=history, logger=logger)

# Test RESTORE commands
test_ucodes = [
    "[SYSTEM|RESTORE*LIST]",
    "[SYSTEM|RESTORE]",
]

for ucode in test_ucodes:
    print(f"\n{'='*60}")
    print(f"Testing: {ucode}")
    print('='*60)
    try:
        result = command_handler.handle_command(ucode, grid, parser)
        print(result)
    except Exception as e:
        import traceback
        print(f"Exception: {e}")
        traceback.print_exc()
    print()
