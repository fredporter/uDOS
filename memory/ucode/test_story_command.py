#!/usr/bin/env python3
"""
Quick test script for STORY command handler
Tests that the handler is properly integrated
"""

import sys
sys.path.insert(0, '/Users/fredbook/Code/uDOS')

from core.commands.story_handler import StoryHandler

print("=" * 60)
print("STORY Command Integration Test")
print("=" * 60)
print()

# Create handler with minimal components
components = {
    'config': None,
    'logger': None,
    'output': None
}

handler = StoryHandler(components)

# Test 1: LIST command
print("Test 1: LIST available adventures")
print("-" * 60)
result = handler.handle('LIST', [])
print(result)
print()

# Test 2: HELP command
print("Test 2: HELP command")
print("-" * 60)
result = handler.handle('HELP', [])
print(result)
print()

print("=" * 60)
print("✅ STORY handler initialized successfully!")
print("=" * 60)
