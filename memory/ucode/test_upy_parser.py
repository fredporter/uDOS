#!/usr/bin/env python3
"""
Test script for .upy adventure parser

Tests parsing of water_quest.upy and validates event structure
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.services.game.upy_adventure_parser import parse_upy_adventure

print("=" * 70)
print("UPY Adventure Parser Test")
print("=" * 70)
print()

# Test file
test_file = "sandbox/ucode/adventures/water_quest.upy"

print(f"Parsing: {test_file}")
print("-" * 70)

try:
    result = parse_upy_adventure(test_file)

    print(f"✅ Parse successful!")
    print()

    # Show metadata
    print("METADATA:")
    print(f"  Name: {result['metadata']['name']}")
    print(f"  Description: {result['metadata']['description']}")
    print()

    # Show labels
    print(f"LABELS FOUND: {len(result['labels'])}")
    for label, line_num in sorted(result['labels'].items(), key=lambda x: x[1])[:10]:
        print(f"  {label:30} (line {line_num + 1})")
    if len(result['labels']) > 10:
        print(f"  ... and {len(result['labels']) - 10} more")
    print()

    # Show events
    print(f"EVENTS CREATED: {len(result['events'])}")
    for i, event in enumerate(result['events'][:10]):
        event_type = event.get('type', 'unknown')
        content = event.get('content', '')[:50]
        effects = len(event.get('effects', []))

        print(f"  Event {i + 1}: {event_type:12} | {content:50} | {effects} effects")

        # Show choices
        if event_type == 'choice':
            for j, choice in enumerate(event.get('choices', [])):
                print(f"    Choice {j + 1}: {choice['text'][:40]:40} → {choice['next_event']}")

    if len(result['events']) > 10:
        print(f"  ... and {len(result['events']) - 10} more events")
    print()

    # Show variables
    print(f"VARIABLES INITIALIZED: {len(result['variables'])}")
    for var, value in list(result['variables'].items())[:10]:
        print(f"  {var:25} = {value}")
    if len(result['variables']) > 10:
        print(f"  ... and {len(result['variables']) - 10} more")
    print()

    # Show flags
    print(f"FLAGS AVAILABLE: {len(result['flags'])}")
    for flag in list(result['flags'])[:10]:
        print(f"  {flag}")
    if len(result['flags']) > 10:
        print(f"  ... and {len(result['flags']) - 10} more")
    print()

    # Save parsed output for inspection
    output_file = "sandbox/drafts/parsed_water_quest.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"📄 Full parsed output saved to: {output_file}")
    print()

    print("=" * 70)
    print("✅ Parser test complete!")
    print("=" * 70)

except Exception as e:
    print(f"❌ Parse failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
