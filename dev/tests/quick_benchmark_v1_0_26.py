#!/usr/bin/env python3
"""
v1.0.26 Quick Performance Check

Simple performance baseline using timing of key operations.
"""

import time
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_imports():
    """Time module imports"""
    start = time.perf_counter()

    from core.uDOS_parser import Parser
    from core.uDOS_commands import CommandHandler
    from core.uDOS_logger import Logger

    end = time.perf_counter()
    return (end - start) * 1000

def test_parser():
    """Time parser initialization"""
    from core.uDOS_parser import Parser

    start = time.perf_counter()
    parser = Parser()
    end = time.perf_counter()

    return (end - start) * 1000

def test_command_handler():
    """Time command handler initialization"""
    from core.uDOS_commands import CommandHandler

    start = time.perf_counter()
    handler = CommandHandler(theme='dungeon')
    end = time.perf_counter()

    return (end - start) * 1000

def main():
    print("="*60)
    print("🚀 uDOS v1.0.26 Quick Performance Baseline")
    print("="*60)
    print()

    results = {}

    # Test imports
    print("⏱️  Testing core imports...")
    results['imports'] = test_imports()
    print(f"   ✓ {results['imports']:.2f}ms")
    print()

    # Test parser
    print("⏱️  Testing parser initialization...")
    results['parser'] = test_parser()
    print(f"   ✓ {results['parser']:.2f}ms")
    print()

    # Test command handler
    print("⏱️  Testing command handler initialization...")
    results['command_handler'] = test_command_handler()
    print(f"   ✓ {results['command_handler']:.2f}ms")
    print()

    # Summary
    print("="*60)
    print("📊 BASELINE SUMMARY")
    print("="*60)
    print()

    total = sum(results.values())
    print(f"Total Initialization Time: {total:.2f}ms")
    print()

    for component, ms in results.items():
        pct = (ms / total) * 100
        print(f"  • {component}: {ms:.2f}ms ({pct:.1f}%)")

    print()

    # Performance assessment
    if total < 100:
        print("✅ EXCELLENT: Core initialization <100ms")
    elif total < 500:
        print("🟡 GOOD: Core initialization <500ms")
    else:
        print("⚠️  SLOW: Core initialization >500ms")

    print()
    print("="*60)
    print("\n✅ Baseline complete!")

if __name__ == "__main__":
    main()
