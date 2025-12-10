#!/usr/bin/env python3
"""
Test smart prompt completion menu display in real terminal.
This will show what the user actually sees.

Run: python dev/tools/test_prompt_display.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def main():
    """Test the actual prompt display."""
    print("=" * 70)
    print("SMART PROMPT DISPLAY TEST")
    print("=" * 70)
    print("\nThis will start an interactive prompt.")
    print("Try typing 'r' and you should see:")
    print("  - Multiple commands (READ, REBOOT, REPAIR, etc.)")
    print("  - Use ↑/↓ or 8/2 to navigate")
    print("  - Press Ctrl+C to exit")
    print("\n" + "=" * 70 + "\n")
    
    try:
        from core.input.smart_prompt import SmartPrompt
        from core.ui.tui_controller import TUIController
        from core.ui.tui_config import get_tui_config
        
        # Initialize TUI
        tui_config = get_tui_config()
        tui = TUIController(tui_config)
        tui.keypad.enabled = True  # Enable keypad
        
        # Create smart prompt
        prompt = SmartPrompt(use_fallback=False)
        prompt.set_tui_controller(tui)
        
        print("✅ Smart prompt initialized")
        print("✅ Keypad enabled")
        print("\nType 'r' to see completions, or 'exit' to quit:\n")
        
        while True:
            try:
                user_input = prompt.ask(prompt_text="🌀 ")
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Exiting test")
                    break
                
                if user_input:
                    print(f"You entered: {user_input}")
                    
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Exiting test")
                break
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
