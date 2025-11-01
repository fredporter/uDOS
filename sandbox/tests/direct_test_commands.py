#!/usr/bin/env python3
"""
Direct test of v1.0.1 system commands
Tests HELP, STATUS, REPAIR without full uDOS initialization
"""

import sys
import os

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Import the handler
from core.commands.system_handler import SystemCommandHandler

# Create a minimal mock environment
class MockConnection:
    def get_mode(self):
        return "ONLINE"

class MockViewport:
    def get_grid_specs(self):
        return {
            'terminal_width': 80,
            'terminal_height': 24,
            'device_type': 'DESKTOP'
        }
    def draw_viewport_map(self):
        return "Viewport visualization here"

class MockUserManager:
    def __init__(self):
        self.user_data = {
            'USER_PROFILE': {
                'NAME': 'TestUser'
            }
        }

class MockHistory:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

# Initialize handler
print("="*60)
print("Testing v1.0.1 System Commands")
print("="*60)
print()

handler = SystemCommandHandler(
    theme='dungeon',
    connection=MockConnection(),
    viewport=MockViewport(),
    user_manager=MockUserManager(),
    history=MockHistory()
)

# Test 1: HELP command
print("TEST 1: HELP Command (full list)")
print("-" * 60)
result = handler.handle_help([], None, None)
print(result[:1000])  # First 1000 chars
print("... (truncated)")
print()

# Test 2: HELP for specific command
print("TEST 2: HELP STATUS")
print("-" * 60)
result = handler.handle_help(['STATUS'], None, None)
print(result)
print()

# Test 3: STATUS command
print("TEST 3: STATUS Command")
print("-" * 60)
result = handler.handle_status([], None, None)
print(result)
print()

# Test 4: REPAIR check mode
print("TEST 4: REPAIR --check")
print("-" * 60)
result = handler.handle_repair(['--check'], None, None)
print(result)
print()

# Test 5: VIEWPORT
print("TEST 5: VIEWPORT Command")
print("-" * 60)
result = handler.handle_viewport([], None, None)
print(result)
print()

print("="*60)
print("✅ All tests completed!")
print("="*60)
