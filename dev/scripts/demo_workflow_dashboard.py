#!/usr/bin/env python3
"""
Demo script for enhanced STATUS dashboard with workflow/mission integration.

Shows different mission states:
1. No active mission (idle)
2. Active mission in EXECUTE phase
3. Active mission in MONITOR phase (near completion)
4. Mission history display
"""

import json
import os
import subprocess
from pathlib import Path

def backup_state():
    """Backup current workflow state."""
    state_file = Path("memory/workflows/state/current.json")
    backup_file = Path("memory/workflows/state/current_demo_backup.json")

    if state_file.exists():
        with open(state_file, 'r') as f:
            state = json.load(f)
        with open(backup_file, 'w') as f:
            json.dump(state, f, indent=2)
        print("✅ Backed up current state")
    else:
        print("⚠️  No state file to backup")

def restore_state():
    """Restore original workflow state."""
    state_file = Path("memory/workflows/state/current.json")
    backup_file = Path("memory/workflows/state/current_demo_backup.json")

    if backup_file.exists():
        with open(backup_file, 'r') as f:
            state = json.load(f)
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        backup_file.unlink()
        print("✅ Restored original state")
    else:
        print("⚠️  No backup to restore")

def set_state(state_data):
    """Set workflow state for demo."""
    state_file = Path("memory/workflows/state/current.json")
    with open(state_file, 'w') as f:
        json.dump(state_data, f, indent=2)

def show_status():
    """Run STATUS command and display output."""
    result = subprocess.run(
        ["./start_udos.sh", "-c", "STATUS"],
        capture_output=True,
        text=True,
        cwd="/Users/fredbook/Code/uDOS"
    )

    # Extract MISSION CONTROL section
    output = result.stdout
    lines = output.split('\n')

    # Find mission control section
    start_idx = None
    end_idx = None

    for i, line in enumerate(lines):
        if 'MISSION CONTROL' in line:
            start_idx = i - 1  # Include border
        elif start_idx and 'SYSTEM STATUS' in line:
            end_idx = i - 1  # Include border before next section
            break

    if start_idx and end_idx:
        mission_section = '\n'.join(lines[start_idx:end_idx])
        print(mission_section)
    else:
        print("❌ Could not find MISSION CONTROL section")

def demo_idle_state():
    """Demo 1: No active mission."""
    print("\n" + "="*80)
    print("DEMO 1: Idle State (No Active Mission)")
    print("="*80 + "\n")

    state = {
        "current_mission": None,
        "status": "IDLE",
        "last_active": None,
        "missions_total": 0,
        "missions_completed": 0,
        "missions_failed": 0,
        "perfect_streak": 0,
        "total_xp_earned": 0,
        "checkpoints_saved": 0,
        "achievements_unlocked": []
    }

    set_state(state)
    show_status()

def demo_active_execute():
    """Demo 2: Active mission in EXECUTE phase."""
    print("\n" + "="*80)
    print("DEMO 2: Active Mission - EXECUTE Phase (81% complete)")
    print("="*80 + "\n")

    state = {
        "current_mission": {
            "id": "knowledge-gen-001",
            "name": "Knowledge Bank Generation",
            "status": "ACTIVE",
            "progress": "45/55",
            "phase": "EXECUTE",
            "elapsed_time": 3725,
            "start_time": "2025-12-03T18:30:00Z",
            "objective": "Generate comprehensive survival guides",
            "last_checkpoint": "auto-checkpoint-40"
        },
        "status": "ACTIVE",
        "last_active": "2025-12-03T20:55:00Z",
        "missions_total": 8,
        "missions_completed": 6,
        "missions_failed": 1,
        "perfect_streak": 3,
        "total_xp_earned": 750,
        "checkpoints_saved": 47,
        "achievements_unlocked": ["FIRST_MISSION", "PERFECTIONIST", "CHECKPOINT_MASTER"]
    }

    set_state(state)
    show_status()

def demo_active_monitor():
    """Demo 3: Active mission in MONITOR phase (near completion)."""
    print("\n" + "="*80)
    print("DEMO 3: Active Mission - MONITOR Phase (95% complete)")
    print("="*80 + "\n")

    state = {
        "current_mission": {
            "id": "svg-batch-gen-042",
            "name": "SVG Diagram Batch Generation",
            "status": "ACTIVE",
            "progress": "190/200",
            "phase": "MONITOR",
            "elapsed_time": 5640,
            "start_time": "2025-12-03T17:00:00Z",
            "objective": "Generate 200 survival diagrams",
            "last_checkpoint": "auto-checkpoint-190"
        },
        "status": "ACTIVE",
        "last_active": "2025-12-03T20:55:00Z",
        "missions_total": 12,
        "missions_completed": 10,
        "missions_failed": 1,
        "perfect_streak": 5,
        "total_xp_earned": 1250,
        "checkpoints_saved": 95,
        "achievements_unlocked": ["FIRST_MISSION", "PERFECTIONIST", "CHECKPOINT_MASTER", "MARATHON"]
    }

    set_state(state)
    show_status()

def demo_history():
    """Demo 4: Mission history (no active mission but rich history)."""
    print("\n" + "="*80)
    print("DEMO 4: Mission History (Rich Stats, No Active Mission)")
    print("="*80 + "\n")

    state = {
        "current_mission": None,
        "status": "IDLE",
        "last_active": "2025-12-03T19:30:00Z",
        "missions_total": 25,
        "missions_completed": 22,
        "missions_failed": 3,
        "perfect_streak": 8,
        "total_xp_earned": 3400,
        "checkpoints_saved": 312,
        "achievements_unlocked": [
            "FIRST_MISSION",
            "PERFECTIONIST",
            "CHECKPOINT_MASTER",
            "MARATHON",
            "SPEEDRUN"
        ]
    }

    set_state(state)
    show_status()

def main():
    """Run all demos."""
    print("\n🎬 Enhanced STATUS Dashboard - Workflow/Mission Integration Demo")
    print("=" * 80)

    # Backup current state
    backup_state()

    try:
        # Run demos
        demo_idle_state()
        input("\n⏸️  Press Enter to continue to next demo...")

        demo_active_execute()
        input("\n⏸️  Press Enter to continue to next demo...")

        demo_active_monitor()
        input("\n⏸️  Press Enter to continue to next demo...")

        demo_history()

    finally:
        # Restore original state
        print("\n" + "="*80)
        restore_state()
        print("\n✅ Demo complete! Original state restored.")
        print("\n💡 The STATUS dashboard now shows:")
        print("   • Active mission status with emoji indicators")
        print("   • Visual progress bars (█░ blocks)")
        print("   • Lifecycle step visualization (✅ ⚡ ⭕)")
        print("   • Runtime tracking (HH:MM:SS)")
        print("   • Checkpoint history")
        print("   • Mission stats (completed/failed/total)")
        print("   • Gameplay integration (XP, perfect streaks)")

if __name__ == "__main__":
    main()
