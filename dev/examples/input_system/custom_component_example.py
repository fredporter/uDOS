#!/usr/bin/env python3
"""
Custom Component Example - Universal Input Device System (v1.2.25)

Demonstrates:
- Building custom components using input APIs
- Combining multiple input handlers
- State management
- Event callbacks
- Hybrid input modes

Usage:
    python examples/input_system/custom_component_example.py
"""

import sys
from pathlib import Path
from typing import List, Callable, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.ui.selector_framework import (
    SelectorFramework,
    SelectableItem,
    SelectorConfig,
    SelectionMode
)
from core.input.keypad_handler import KeypadHandler, KeypadMode
from core.input.mouse_handler import MouseHandler, ClickableRegion, MouseEvent
from core.services.device_manager import DeviceManager


class Task:
    """Task item for task manager."""
    
    def __init__(self, title: str, completed: bool = False):
        self.title = title
        self.completed = completed
        self.created_at = datetime.now()
        self.completed_at: Optional[datetime] = None
    
    def toggle(self) -> None:
        """Toggle task completion status."""
        self.completed = not self.completed
        if self.completed:
            self.completed_at = datetime.now()
        else:
            self.completed_at = None


class TaskManager:
    """Custom task manager component with multi-input support."""
    
    def __init__(self):
        """Initialize task manager."""
        self.tasks: List[Task] = []
        self.selector = SelectorFramework(
            config=SelectorConfig(
                mode=SelectionMode.SINGLE,
                page_size=9,
                show_numbers=True,
                show_icons=True
            )
        )
        
        # Input handlers
        self.keypad = KeypadHandler()
        self.keypad.set_mode(KeypadMode.SELECTION)
        
        self.mouse = MouseHandler()
        self.device_manager = DeviceManager()
        
        # Detect capabilities
        self.caps = self.device_manager.detect_input_capabilities()
        self.mouse_enabled = self.caps["mouse"]["available"]
        
        # Initialize with sample tasks
        self._create_sample_tasks()
        self.load_tasks()
    
    def _create_sample_tasks(self) -> None:
        """Create sample tasks."""
        self.tasks = [
            Task("Review code changes", completed=True),
            Task("Write documentation"),
            Task("Run test suite"),
            Task("Update dependencies"),
            Task("Fix bug #123"),
        ]
    
    def load_tasks(self) -> None:
        """Load tasks into selector."""
        items = []
        
        for i, task in enumerate(self.tasks):
            icon = "✓" if task.completed else "○"
            label = task.title
            if task.completed:
                label = f"~{label}~"  # Strikethrough effect
            
            items.append(SelectableItem(
                id=f"task_{i}",
                label=label,
                icon=icon,
                metadata={"index": i, "task": task}
            ))
        
        self.selector.set_items(items)
        self.keypad.set_items([item.label for item in items])
    
    def display(self) -> None:
        """Display task manager."""
        print("\033[2J\033[H")  # Clear screen
        
        # Header
        print("=" * 70)
        print("✅ TASK MANAGER")
        print("=" * 70)
        print()
        
        # Statistics
        completed = sum(1 for t in self.tasks if t.completed)
        total = len(self.tasks)
        percent = (completed / total * 100) if total > 0 else 0
        
        print(f"Progress: {completed}/{total} tasks completed ({percent:.0f}%)")
        print()
        
        # Task list
        if not self.tasks:
            print("  No tasks yet. Press 'n' to add a task.")
        else:
            lines = self.selector.display()
            for line in lines:
                print(line)
        
        print()
        print("-" * 70)
        
        # Current task details
        if self.tasks:
            current = self.selector.get_current_item()
            if current:
                task = current.metadata["task"]
                print(f"\nTask: {task.title}")
                print(f"Status: {'✓ Completed' if task.completed else '○ Pending'}")
                print(f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
                if task.completed_at:
                    print(f"Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M')}")
        
        print()
        print("-" * 70)
        
        # Controls
        print()
        print("Controls:")
        print("  1-9      Select task")
        print("  ↑/↓      Navigate (8/2 on keypad)")
        print("  Space    Toggle completion (5 on keypad)")
        print("  n        New task")
        print("  d        Delete task")
        print("  c        Clear completed")
        print("  q        Quit")
        
        if self.mouse_enabled:
            print("  Mouse    Click to select/toggle")
        
        print()
    
    def handle_input(self, key: str) -> bool:
        """Handle user input.
        
        Args:
            key: Input key
            
        Returns:
            True to continue, False to quit
        """
        if key == 'q':
            return False
        
        elif key == 'n':
            self.add_task()
        
        elif key == 'd':
            self.delete_current_task()
        
        elif key == 'c':
            self.clear_completed()
        
        elif key in '123456789':
            result = self.keypad.handle_key(key)
            if result:
                self.select_by_label(result)
        
        elif key in ['8', 'w']:  # Up
            self.selector.navigate_up()
        
        elif key in ['2', 's']:  # Down
            self.selector.navigate_down()
        
        elif key in ['5', ' ', '\r', '\n']:  # Toggle
            self.toggle_current_task()
        
        return True
    
    def select_by_label(self, label: str) -> None:
        """Select task by label.
        
        Args:
            label: Task label
        """
        for item in self.selector.items:
            if item.label == label:
                self.selector.navigate_to(item.id)
                break
    
    def toggle_current_task(self) -> None:
        """Toggle current task completion status."""
        if not self.tasks:
            return
        
        current = self.selector.get_current_item()
        if current:
            task = current.metadata["task"]
            task.toggle()
            self.load_tasks()
    
    def add_task(self) -> None:
        """Add new task."""
        print("\n📝 New Task")
        title = input("Task title: ").strip()
        
        if title:
            self.tasks.append(Task(title))
            self.load_tasks()
            print("✓ Task added!")
        else:
            print("✗ Task title cannot be empty")
        
        input("\nPress Enter to continue...")
    
    def delete_current_task(self) -> None:
        """Delete currently selected task."""
        if not self.tasks:
            return
        
        current = self.selector.get_current_item()
        if current:
            task = current.metadata["task"]
            print(f"\n⚠️  Delete task: {task.title}?")
            confirm = input("Type 'yes' to confirm: ").strip().lower()
            
            if confirm == 'yes':
                index = current.metadata["index"]
                self.tasks.pop(index)
                self.load_tasks()
                print("✓ Task deleted")
            else:
                print("✗ Deletion cancelled")
            
            input("\nPress Enter to continue...")
    
    def clear_completed(self) -> None:
        """Clear all completed tasks."""
        completed_count = sum(1 for t in self.tasks if t.completed)
        
        if completed_count == 0:
            print("\n✗ No completed tasks to clear")
            input("Press Enter to continue...")
            return
        
        print(f"\n⚠️  Clear {completed_count} completed task(s)?")
        confirm = input("Type 'yes' to confirm: ").strip().lower()
        
        if confirm == 'yes':
            self.tasks = [t for t in self.tasks if not t.completed]
            self.load_tasks()
            print(f"✓ Cleared {completed_count} completed task(s)")
        else:
            print("✗ Clear cancelled")
        
        input("\nPress Enter to continue...")
    
    def run(self) -> None:
        """Run task manager main loop."""
        print("🚀 Starting Task Manager...")
        print(f"Input capabilities: Keypad=✓, Mouse={'✓' if self.mouse_enabled else '✗'}")
        print()
        print("This is a custom component built using the Universal Input Device System.")
        print("It demonstrates combining selector, keypad, and mouse handlers.")
        input("\nPress Enter to continue...")
        
        while True:
            self.display()
            
            try:
                key = input("Command: ").strip().lower()
                if not key:
                    continue
                
                if not self.handle_input(key[0]):
                    break
                    
            except KeyboardInterrupt:
                break
        
        print("\n👋 Goodbye!")


def main():
    """Main entry point."""
    try:
        manager = TaskManager()
        manager.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
