#!/usr/bin/env python3
"""
TUI Smart Input Interactive Demo (v1.2.22)
Demonstrates the fixed numpad navigation and completion features.

Run: python dev/tools/demo_smart_input.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def print_demo_header():
    """Print demo header."""
    print("\n" + "=" * 70)
    print("TUI SMART INPUT INTERACTIVE DEMO (v1.2.22)")
    print("=" * 70)
    print("\nThis demo shows the improved numpad navigation behavior:")
    print("• When completion menu is OPEN → numpad navigates (8↑ 2↓ 5✓)")
    print("• When buffer is EMPTY → numpad navigates history/pager")
    print("• When typing text (no menu) → numpad inserts digits")
    print("\n" + "=" * 70 + "\n")


def demo_scenario_1():
    """Demo: Navigating completion menu with numpad."""
    print("📋 SCENARIO 1: Navigating Completions with Numpad")
    print("-" * 70)
    print("""
1. User types: R
2. Completion menu opens showing: READ, REBOOT, REPAIR, RUN, etc.
3. User presses: 8 (numpad up)
   → Navigates to previous completion ✅
4. User presses: 2 (numpad down)  
   → Navigates to next completion ✅
5. User presses: 5 (numpad select)
   → Accepts selected completion ✅

BEFORE (v1.2.21): Numpad 8 would insert "8" → "R8" ❌
AFTER  (v1.2.22): Numpad 8 navigates menu ✅
    """)


def demo_scenario_2():
    """Demo: Typing numbers when no menu open."""
    print("\n📋 SCENARIO 2: Typing Numbers (No Menu Open)")
    print("-" * 70)
    print("""
1. User types: XP
2. Completion menu auto-dismisses (no more matches)
3. User presses: Space
4. User presses: 1 0 0 (numpad)
   → Inserts "100" → "XP 100" ✅
5. User presses: Enter
   → Executes: XP 100

BEFORE (v1.2.21): After "XP ", pressing 1 would insert "1" ✅ (worked)
AFTER  (v1.2.22): Same behavior ✅
    """)


def demo_scenario_3():
    """Demo: Empty buffer navigation."""
    print("\n📋 SCENARIO 3: Empty Buffer Navigation")
    print("-" * 70)
    print("""
1. Prompt is empty: 🌀 _
2. User presses: 8 (numpad up)
   → Navigates to previous command in history ✅
3. User presses: 2 (numpad down)
   → Navigates to next command in history ✅
4. User presses: 1 (numpad history back)
   → Goes back in history ✅
5. User presses: 5 (numpad select)
   → Submits current command ✅

BEFORE (v1.2.21): Worked correctly ✅
AFTER  (v1.2.22): Same behavior ✅
    """)


def demo_scenario_4():
    """Demo: Tab and Esc keys."""
    print("\n📋 SCENARIO 4: Tab and Esc Keys")
    print("-" * 70)
    print("""
1. User types: R
2. Completion menu shows automatically
3. User presses: Tab
   → Navigates to next completion ✅
4. User presses: Esc
   → Closes completion menu ✅
5. User continues typing: E
6. Completion menu reopens showing: READ, REBOOT, etc.
7. User presses: Tab
   → Selects REBOOT ✅

BEFORE (v1.2.21): Tab behavior unclear
AFTER  (v1.2.22): Tab navigates/triggers, Esc closes ✅
    """)


def demo_priority_logic():
    """Demo: Priority logic explanation."""
    print("\n📋 PRIORITY LOGIC (How Numpad 8/2/5 Work)")
    print("-" * 70)
    print("""
Priority 1: Completion Menu Open
├─ Numpad 8 → Navigate UP in menu
├─ Numpad 2 → Navigate DOWN in menu
└─ Numpad 5 → ACCEPT selected item

Priority 2: Buffer Empty (No Menu)
├─ Numpad 8 → Previous command in HISTORY
├─ Numpad 2 → Next command in HISTORY
└─ Numpad 5 → SUBMIT command

Priority 3: Text Present (No Menu)
├─ Numpad 8 → Insert "8"
├─ Numpad 2 → Insert "2"
└─ Numpad 5 → Insert "5"

This ensures:
• Completion navigation ALWAYS works when menu is visible
• History navigation works when starting fresh
• Number input works when typing commands with numeric args
    """)


def demo_visual_guide():
    """Demo: Visual state guide."""
    print("\n📋 VISUAL STATE GUIDE")
    print("-" * 70)
    print("""
STATE 1: Empty Prompt (Numpad = Navigation)
┌────────────────────────────────────────────┐
│ 🌀 _                                       │ ← Empty
│                                            │
└────────────────────────────────────────────┘
Actions: 8↑ 2↓ = History | 5✓ = Submit

STATE 2: Typing with Menu (Numpad = Navigate Menu)
┌────────────────────────────────────────────┐
│ 🌀 R_                                      │ ← Typed "R"
│   ► READ      - Read and analyze panel    │ ← Selected
│     REBOOT    - Restart uDOS              │
│     REPAIR    - System health check       │
│     RUN       - Execute script            │
└────────────────────────────────────────────┘
Actions: 8↑ 2↓ = Navigate | 5✓ = Accept | Esc = Close

STATE 3: Typing (No Menu) (Numpad = Insert Digits)
┌────────────────────────────────────────────┐
│ 🌀 XP _                                    │ ← No matches
│                                            │
└────────────────────────────────────────────┘
Actions: 8 = "8" | 2 = "2" | 5 = "5" (insert text)
    """)


def demo_keyboard_shortcuts():
    """Demo: Complete keyboard shortcuts."""
    print("\n📋 COMPLETE KEYBOARD REFERENCE")
    print("-" * 70)
    print("""
NAVIGATION (When Menu Open)
├─ ↑/↓ or 8/2    → Navigate completions
├─ →/Tab or 6    → Accept selected
├─ Esc           → Close menu
└─ 5             → Accept selected

NAVIGATION (When Buffer Empty)
├─ ↑/↓ or 8/2    → Navigate history
├─ 1/3           → History back/forward
├─ 4/6           → Pager scroll
├─ 5             → Submit command
└─ 0             → Toggle file browser

TEXT INPUT (When Typing, No Menu)
├─ 0-9           → Insert digits
├─ Letters       → Type command
├─ Ctrl+A        → Start of line
├─ Ctrl+E        → End of line
├─ Ctrl+K        → Delete to end
├─ Ctrl+U        → Delete to start
├─ Backspace     → Delete char
└─ Tab           → Trigger completions
    """)


def main():
    """Run demo."""
    print_demo_header()
    
    demo_scenario_1()
    demo_scenario_2()
    demo_scenario_3()
    demo_scenario_4()
    demo_priority_logic()
    demo_visual_guide()
    demo_keyboard_shortcuts()
    
    print("\n" + "=" * 70)
    print("END OF DEMO")
    print("=" * 70)
    print("\nTo test interactively:")
    print("1. Activate venv: source .venv/bin/activate")
    print("2. Run uDOS: ./start_udos.sh")
    print("3. Enable keypad: TUI ENABLE KEYPAD")
    print("4. Try typing 'R' and using numpad 8/2 to navigate")
    print("\n")


if __name__ == '__main__':
    main()
