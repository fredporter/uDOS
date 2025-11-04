#!/usr/bin/env python3
"""Test RESTORE command parsing"""

import sys
sys.path.insert(0, '/Users/fredbook/Code/uDOS')

from core.uDOS_parser import Parser

parser = Parser()

# Test RESTORE commands
test_cases = [
    "RESTORE",
    "RESTORE LIST",
    "RESTORE 42",
    "UNDO",
    "REDO"
]

for test in test_cases:
    result = parser.parse(test)
    print(f"{test:20} -> {result}")
