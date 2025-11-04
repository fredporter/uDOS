#!/usr/bin/env python3
"""
Test OK ASK/DEV command differentiation
"""

import sys
sys.path.insert(0, '/Users/fredbook/Code/uDOS')

from core.commands.assistant_handler import AssistantCommandHandler
from core.uDOS_grid import Grid

# Initialize handler
handler = AssistantCommandHandler(theme='dungeon')
grid = Grid()

print("=" * 60)
print("Testing OK Command Implementation")
print("=" * 60)

# Test 1: OK without parameters
print("\n[TEST 1] OK (no parameters - should show help)")
print("-" * 60)
result = handler.handle("OK", [], grid)
print(result)

# Test 2: OK ASK
print("\n[TEST 2] OK ASK <question>")
print("-" * 60)
result = handler.handle("OK", ["ASK", "what", "is", "uDOS?"], grid)
print(result)

# Test 3: OK DEV
print("\n[TEST 3] OK DEV <task>")
print("-" * 60)
result = handler.handle("OK", ["DEV", "create", "a", "command", "handler"], grid)
print(result)

# Test 4: Invalid subcommand
print("\n[TEST 4] OK INVALID")
print("-" * 60)
result = handler.handle("OK", ["INVALID", "test"], grid)
print(result)

# Test 5: Legacy ASK command (backward compatibility)
print("\n[TEST 5] ASK <question> (legacy)")
print("-" * 60)
result = handler.handle("ASK", ["what", "is", "uDOS?"], grid)
print(result)

print("\n" + "=" * 60)
print("Tests Complete")
print("=" * 60)
