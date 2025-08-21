#!/usr/bin/env python3
"""
uDOS Sorcerer Web Integration Bridge
Provides a simple interface for uDOS UI to call web commands
"""

import sys
import json
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_commands import uDOSSorcererCommands

def main():
    """Main entry point for uDOS web integration"""
    
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python3 web_bridge.py <command> [args...]",
            "available_commands": [
                "web.test",
                "web.scrape <url> <selectors_json>",
                "web.links <url> [filter]",
                "web.images <url>",
                "web.metadata <url>",
                "web.download <url> [filename]",
                "web.api <url> [method] [data]",
                "web.help"
            ]
        }, indent=2))
        return
    
    commander = uDOSSorcererCommands()
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    try:
        result = commander.execute(command, args)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e),
            "command": command,
            "args": args
        }, indent=2))

if __name__ == "__main__":
    main()
