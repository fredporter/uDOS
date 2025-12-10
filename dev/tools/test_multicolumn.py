#!/usr/bin/env python3
"""
Minimal test of MULTI_COLUMN completion display.
This will help diagnose if the issue is with our code or prompt_toolkit configuration.
"""

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle

class SimpleCompleter(Completer):
    """Simple test completer."""
    
    def get_completions(self, document, complete_event):
        """Return multiple completions for testing."""
        text = document.text_before_cursor
        
        # Test commands
        commands = [
            'READ', 'REBOOT', 'REPAIR', 'REPORT', 'ROLE', 
            'RUN', 'REDO', 'RESTORE', 'RENAME', 'RESOURCE'
        ]
        
        for cmd in commands:
            if cmd.startswith(text.upper()):
                yield Completion(
                    cmd,
                    start_position=-len(text),
                    display=f"{cmd:<12} - Test command"
                )

def main():
    print("=" * 70)
    print("MULTI_COLUMN COMPLETION TEST")
    print("=" * 70)
    print("\nType 'r' or 're' and you should see ALL matching commands")
    print("in a multi-column layout.")
    print("\nPress Ctrl+C to exit\n")
    print("=" * 70 + "\n")
    
    completer = SimpleCompleter()
    
    session = PromptSession(
        completer=completer,
        complete_while_typing=True,
        complete_style=CompleteStyle.MULTI_COLUMN,
        reserve_space_for_menu=12,
    )
    
    while True:
        try:
            result = session.prompt('Test> ')
            print(f"You entered: {result}")
            if result.lower() in ['exit', 'quit', 'q']:
                break
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == '__main__':
    main()
