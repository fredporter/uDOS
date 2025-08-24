#!/usr/bin/env python3
"""
uDOS CLI Server (Ghost/Tomb roles)
Enhanced CLI-only interface for limited-access roles with proper command integration.
"""
import subprocess
import sys
import os
import json
import re
from pathlib import Path

# Set up paths
UDOS_ROOT = Path(__file__).parent.parent.parent
EXTENSIONS_DIR = UDOS_ROOT / "extensions"
UCORE_CODE_DIR = UDOS_ROOT / "uCORE" / "code"
UMEMORY_DIR = UDOS_ROOT / "uMEMORY"
COMMANDS_FILE = UMEMORY_DIR / "system" / "uDATA-commands.json"

class CLIServer:
    def __init__(self):
        self.role = self.detect_role()
        self.commands = self.load_commands()
        self.setup_environment()

    def detect_role(self):
        """Detect user role from installation.md"""
        install_file = UMEMORY_DIR / "user" / "installation.md"
        if install_file.exists():
            with open(install_file, 'r') as f:
                for line in f:
                    if line.lower().startswith('role:'):
                        return line.split(':', 1)[1].strip().lower()
        return 'ghost'  # Default to most restrictive

    def load_commands(self):
        """Load available commands from uDATA format"""
        commands = {}

        # Add built-in CLI commands first
        commands.update({
            'HELP': {'command': 'HELP', 'role_access': 0, 'description': 'Show help information'},
            'STATUS': {'command': 'STATUS', 'role_access': 0, 'description': 'Show system status'},
            'COMMANDS': {'command': 'COMMANDS', 'role_access': 0, 'description': 'List available commands'},
            'INFO': {'command': 'INFO', 'role_access': 0, 'description': 'Show system information'}
        })

        # Load core commands
        if COMMANDS_FILE.exists():
            try:
                with open(COMMANDS_FILE, 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('{'):
                            cmd_data = json.loads(line)
                            if 'command' in cmd_data:
                                commands[cmd_data['command']] = cmd_data
            except Exception as e:
                print(f"Warning: Could not load commands: {e}")

        # Load extension commands from uCORE
        if UCORE_CODE_DIR.exists():
            for cmd_file in UCORE_CODE_DIR.rglob("uDATA-commands.json"):
                try:
                    with open(cmd_file, 'r') as f:
                        for line in f:
                            if line.strip() and not line.startswith('{'):
                                cmd_data = json.loads(line)
                                if 'command' in cmd_data:
                                    commands[cmd_data['command']] = cmd_data
                except Exception:
                    continue

        # Load extension commands from extensions dir
        if EXTENSIONS_DIR.exists():
            for cmd_file in EXTENSIONS_DIR.rglob("uDATA-commands.json"):
                try:
                    with open(cmd_file, 'r') as f:
                        for line in f:
                            if line.strip() and not line.startswith('{'):
                                cmd_data = json.loads(line)
                                if 'command' in cmd_data:
                                    commands[cmd_data['command']] = cmd_data
                except Exception:
                    continue

        return commands

    def setup_environment(self):
        """Setup environment for CLI-only operation"""
        os.environ['UDOS_MODE'] = 'cli'
        os.environ['UDOS_ROLE'] = self.role
        os.environ['UDOS_UI'] = 'false'

        # Set grid limitations based on role
        if self.role in ['ghost', 'tomb']:
            os.environ['UDOS_MAX_GRID'] = '40x16'

    def check_command_access(self, command):
        """Check if role has access to command"""
        if command not in self.commands:
            return False, f"Unknown command: {command}"

        cmd_data = self.commands[command]
        required_access = cmd_data.get('role_access', 0)

        role_levels = {
            'ghost': 10, 'tomb': 20, 'crypt': 30, 'drone': 40,
            'knight': 50, 'imp': 60, 'sorcerer': 80, 'wizard': 100
        }

        user_level = role_levels.get(self.role, 0)

        if user_level < required_access:
            return False, f"Access denied: {command} requires level {required_access}, you have {user_level}"

        return True, "OK"

    def parse_command(self, input_text):
        """Parse uDOS command format [COMMAND*params]"""
        # Handle both [COMMAND] and COMMAND formats
        if input_text.startswith('[') and input_text.endswith(']'):
            inner = input_text[1:-1]
        else:
            inner = input_text

        parts = inner.split('*')
        command = parts[0].upper()  # Convert to uppercase
        params = parts[1:] if len(parts) > 1 else []

        return command, params

    def execute_command(self, command, params):
        """Execute a uDOS command with role-based restrictions"""
        # Check access
        has_access, message = self.check_command_access(command)
        if not has_access:
            print(f"ERROR: {message}")
            return 1

        cmd_data = self.commands[command]

        # Handle different command types
        if 'library' in cmd_data and 'function' in cmd_data:
            return self.execute_library_function(cmd_data, params)
        elif 'script' in cmd_data:
            return self.execute_script(cmd_data['script'], params)
        else:
            # Try to find and execute the command
            return self.execute_direct_command(command, params)

    def execute_library_function(self, cmd_data, params):
        """Execute command from library function"""
        library = cmd_data.get('library', '')
        function = cmd_data.get('function', '')

        # Look for library in extensions
        library_paths = [
            UCORE_CODE_DIR / "*" / "library" / "shell" / library,
            EXTENSIONS_DIR / "user" / "*" / "library" / "shell" / library,
            UDOS_ROOT / "uSCRIPT" / "library" / "shell" / library,
        ]

        for pattern in library_paths:
            for lib_file in UDOS_ROOT.glob(str(pattern)):
                if lib_file.exists():
                    # Source the library and call the function
                    script_cmd = f'source "{lib_file}" && {function} {" ".join(params)}'
                    return self.run_shell_command(script_cmd)

        print(f"ERROR: Library not found: {library}")
        return 1

    def execute_script(self, script_path, params):
        """Execute a script with parameters"""
        if not script_path.startswith('/'):
            # Relative path, search in uDOS directories
            search_paths = [
                UDOS_ROOT / "uSCRIPT",
                EXTENSIONS_DIR,
                UDOS_ROOT / "uCORE" / "code"
            ]

            for search_dir in search_paths:
                full_path = search_dir / script_path
                if full_path.exists():
                    script_path = str(full_path)
                    break

        if not os.path.exists(script_path):
            print(f"ERROR: Script not found: {script_path}")
            return 1

        return self.run_script(script_path, params)

    def execute_direct_command(self, command, params):
        """Execute command directly (fallback)"""
        # Convert to uppercase for consistency
        command = command.upper()

        # For commands like HELP, STATUS, etc.
        if command == "HELP":
            return self.show_help(params)
        elif command == "STATUS":
            return self.show_status()
        elif command == "COMMANDS":
            return self.list_commands()
        else:
            print(f"ERROR: Command implementation not found: {command}")
            return 1

    def run_shell_command(self, cmd):
        """Run a shell command safely"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=UDOS_ROOT)
            if result.stdout:
                print(result.stdout.rstrip())
            if result.stderr:
                print(result.stderr.rstrip(), file=sys.stderr)
            return result.returncode
        except Exception as e:
            print(f"ERROR: {e}")
            return 1

    def run_script(self, script_path, args):
        """Run a script with arguments"""
        if not os.path.isfile(script_path):
            print(f"ERROR: Script not found: {script_path}")
            return 1

        cmd = [script_path] + args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=UDOS_ROOT)
            print(result.stdout.rstrip())
            return 0
        except subprocess.CalledProcessError as e:
            print(f"Script error: {e.stderr.rstrip()}")
            return e.returncode
        except Exception as e:
            print(f"ERROR: {e}")
            return 1

    def show_help(self, params):
        """Show help for commands"""
        if params:
            # Show help for specific command
            command = params[0]
            if command in self.commands:
                cmd_data = self.commands[command]
                print(f"Command: {command}")
                print(f"Syntax: {cmd_data.get('syntax', 'N/A')}")
                print(f"Description: {cmd_data.get('description', 'N/A')}")
                if 'examples' in cmd_data:
                    print("Examples:")
                    for example in cmd_data['examples']:
                        print(f"  {example}")
            else:
                print(f"Unknown command: {command}")
        else:
            # Show available commands for this role
            print(f"Available commands for role '{self.role}':")
            available = []
            for cmd, data in self.commands.items():
                has_access, _ = self.check_command_access(cmd)
                if has_access:
                    available.append(f"  {cmd} - {data.get('description', 'No description')}")

            if available:
                print('\n'.join(sorted(available)))
            else:
                print("  No commands available for your role.")
        return 0

    def show_status(self):
        """Show CLI server status"""
        print(f"uDOS CLI Server Status:")
        print(f"Role: {self.role}")
        print(f"Commands loaded: {len(self.commands)}")
        print(f"Extensions directory: {EXTENSIONS_DIR}")
        print(f"Max grid: {os.environ.get('UDOS_MAX_GRID', 'unlimited')}")
        return 0

    def list_commands(self):
        """List all available commands"""
        available = []
        for cmd, data in self.commands.items():
            has_access, _ = self.check_command_access(cmd)
            if has_access:
                available.append(cmd)

        print("Available commands:")
        for cmd in sorted(available):
            print(f"  {cmd}")
        return 0

    def interactive_mode(self):
        """Run interactive CLI mode"""
        print(f"uDOS CLI Server - Role: {self.role}")
        print("Type 'help' for commands, 'exit' to quit")

        while True:
            try:
                user_input = input("uDOS> ").strip()
                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break

                if user_input.lower() == 'help':
                    self.show_help([])
                    continue

                # Parse and execute command
                command, params = self.parse_command(user_input)
                self.execute_command(command, params)

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                break

def main():
    server = CLIServer()

    if len(sys.argv) < 2:
        # Interactive mode
        server.interactive_mode()
    else:
        # Command mode
        command_text = sys.argv[1]
        command, params = server.parse_command(command_text)
        additional_params = sys.argv[2:] if len(sys.argv) > 2 else []
        all_params = params + additional_params

        exit_code = server.execute_command(command, all_params)
        sys.exit(exit_code)

if __name__ == "__main__":
    main()
