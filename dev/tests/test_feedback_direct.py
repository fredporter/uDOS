#!/usr/bin/env python
"""
Direct test of FEEDBACK and REPORT handlers (bypassing parser)

Tests the feedback system at the handler level.
"""

import sys
from pathlib import Path

# Add uDOS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.commands.user_handler import UserCommandHandler

def test_feedback_handlers():
    """Test FEEDBACK and REPORT handlers directly"""

    print("="*60)
    print("Testing User Feedback Handlers (Direct)")
    print("="*60)
    print()

    # Initialize handler
    handler = UserCommandHandler()

    # Test 1: Simple feedback
    print("--- Test 1: Simple Feedback ---")
    result = handler.handle("FEEDBACK", ["Love the new system!", "praise"])
    print(result)
    print()

    # Test 2: Confusion feedback
    print("--- Test 2: Confusion Feedback ---")
    result = handler.handle("FEEDBACK", ["MAP commands are unclear", "confusion"])
    print(result)
    print()

    # Test 3: Feature request
    print("--- Test 3: Feature Request ---")
    result = handler.handle("FEEDBACK", ["Please add keyboard shortcuts", "request"])
    print(result)
    print()

    # Test 4: Bug report
    print("--- Test 4: Bug Report ---")
    result = handler.handle("REPORT", [
        "Menu text overlaps",  # title
        "Text overlaps in terminals < 80 cols",  # description
        "high",  # severity
        "bug"  # category
    ])
    print(result)
    print()

    # Test 5: Feature request report
    print("--- Test 5: Feature Request Report ---")
    result = handler.handle("REPORT", [
        "Dark mode support",  # title
        "Add dark color theme option for night coding",  # description
        "low",  # severity
        "feature_request"  # category
    ])
    print(result)
    print()

    # Test 6: View recent feedback
    print("--- Test 6: View Feedback Summary ---")
    summary = handler.feedback_handler.get_feedback_summary(limit=5)
    print(summary)
    print()

    # Test 7: View recent reports
    print("--- Test 7: View Reports Summary ---")
    summary = handler.feedback_handler.get_reports_summary(limit=5)
    print(summary)
    print()

    print("="*60)
    print("✅ Direct handler test complete")
    print("="*60)


if __name__ == '__main__':
    test_feedback_handlers()
