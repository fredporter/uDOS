#!/usr/bin/env python
"""
Test script for FEEDBACK and REPORT commands in uDOS v1.1.0

Simulates user input to test the new feedback system integration.
"""

import sys
from pathlib import Path

# Add uDOS to path
sys.path.insert(0, str(Path(__file__).parent))

from core.uDOS_parser import Parser
from core.uDOS_grid import Grid
from core.uDOS_commands import CommandHandler

def test_feedback_integration():
    """Test FEEDBACK and REPORT commands via parser and handler"""

    print("="*60)
    print("Testing uDOS v1.1.0 Feedback System Integration")
    print("="*60)
    print()

    # Initialize components
    parser = Parser()
    grid = Grid()
    handler = CommandHandler()

    # Test 1: FEEDBACK command with praise
    print("--- Test 1: FEEDBACK (praise) ---")
    ucode = parser.parse('FEEDBACK "The new PANEL system is amazing!"')
    print(f"uCODE: {ucode}")
    result = handler.handle_command(ucode, grid, parser)
    print(result)
    print()

    # Test 2: FEEDBACK command with confusion
    print("--- Test 2: FEEDBACK (confusion) ---")
    ucode = parser.parse('FEEDBACK "Not sure how MAP works" TYPE confusion')
    print(f"uCODE: {ucode}")
    result = handler.handle_command(ucode, grid, parser)
    print(result)
    print()

    # Test 3: FEEDBACK command with feature request
    print("--- Test 3: FEEDBACK (feature request) ---")
    ucode = parser.parse('FEEDBACK "Add dark mode" TYPE request')
    print(f"uCODE: {ucode}")
    result = handler.handle_command(ucode, grid, parser)
    print(result)
    print()

    # Test 4: REPORT command with bug
    print("--- Test 4: REPORT (bug) ---")
    ucode = parser.parse('REPORT TITLE="Menu overlap" DESC="Text overlaps in narrow terminals"')
    print(f"uCODE: {ucode}")
    result = handler.handle_command(ucode, grid, parser)
    print(result)
    print()

    # Test 5: REPORT with severity
    print("--- Test 5: REPORT (high severity) ---")
    ucode = parser.parse('REPORT TITLE="MAP CREATE fails" DESC="KeyError on map creation" SEVERITY high')
    print(f"uCODE: {ucode}")
    result = handler.handle_command(ucode, grid, parser)
    print(result)
    print()

    # Test 6: Check feedback files were created
    print("--- Test 6: Verify file creation ---")
    feedback_file = Path("memory/logs/feedback/user_feedback.jsonl")
    reports_file = Path("memory/logs/feedback/bug_reports.jsonl")

    if feedback_file.exists():
        print(f"✅ Feedback file created: {feedback_file}")
        with open(feedback_file, 'r') as f:
            lines = f.readlines()
            print(f"   {len(lines)} feedback entries logged")
    else:
        print(f"❌ Feedback file not found: {feedback_file}")

    if reports_file.exists():
        print(f"✅ Reports file created: {reports_file}")
        with open(reports_file, 'r') as f:
            lines = f.readlines()
            print(f"   {len(lines)} bug reports logged")
    else:
        print(f"❌ Reports file not found: {reports_file}")

    print()
    print("="*60)
    print("✅ Feedback system integration test complete")
    print("="*60)


if __name__ == '__main__':
    test_feedback_integration()
