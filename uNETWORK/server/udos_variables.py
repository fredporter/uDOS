#!/usr/bin/env python3
"""
uDOS Variables Library
Provides Python interface for uDOS variable system integration
Part of: UI Layer Development - Web Dashboard
"""

import json
import subprocess
import os
from typing import Dict, List, Optional, Any

class UDOSVariables:
    """Interface for uDOS variable system from Python"""

    def __init__(self, udos_root: str = None):
        """Initialize with uDOS root directory"""
        self.udos_root = udos_root or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.command_router = os.path.join(self.udos_root, "uCORE", "code", "command-router.sh")

    def get_variable(self, name: str) -> Optional[str]:
        """Get single variable value"""
        try:
            result = subprocess.run(
                [self.command_router, f"[GET|{name}]"],
                capture_output=True,
                text=True,
                cwd=self.udos_root
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                # Parse output for variable value
                if "Value:" in output:
                    return output.split("Value:")[-1].strip()
                return output
            return None
        except Exception as e:
            print(f"Error getting variable {name}: {e}")
            return None

    def set_variable(self, name: str, value: str) -> bool:
        """Set variable value"""
        try:
            result = subprocess.run(
                [self.command_router, f"[SET|{name}*{value}]"],
                capture_output=True,
                text=True,
                cwd=self.udos_root
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error setting variable {name}: {e}")
            return False

    def list_variables(self) -> Dict[str, str]:
        """Get all variables as dictionary"""
        try:
            result = subprocess.run(
                [self.command_router, "[LIST]"],
                capture_output=True,
                text=True,
                cwd=self.udos_root
            )

            variables = {}
            if result.returncode == 0:
                output = result.stdout
                # Parse variable list output
                for line in output.split('\n'):
                    if '$' in line and '=' in line:
                        try:
                            # Extract variable name and value
                            parts = line.split('=', 1)
                            if len(parts) == 2:
                                name = parts[0].strip().replace('$', '').replace('[', '').replace(']', '')
                                value = parts[1].strip()
                                variables[name] = value
                        except:
                            continue

            return variables
        except Exception as e:
            print(f"Error listing variables: {e}")
            return {}

    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute uCODE command and return result"""
        try:
            result = subprocess.run(
                [self.command_router, command],
                capture_output=True,
                text=True,
                cwd=self.udos_root
            )

            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.stderr else None,
                'return_code': result.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'return_code': -1
            }

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            'router_status': 'unknown',
            'variable_count': 0,
            'udos_root': self.udos_root
        }

        # Check if command router exists and is executable
        if os.path.exists(self.command_router) and os.access(self.command_router, os.X_OK):
            status['router_status'] = 'active'

            # Get variable count
            variables = self.list_variables()
            status['variable_count'] = len(variables)
        else:
            status['router_status'] = 'unavailable'

        return status

    def get_role_info(self) -> Dict[str, Any]:
        """Get current user role information"""
        role_result = self.execute_command("[GET|USER-ROLE]")

        # Default role information
        role_data = {
            'name': 'Ghost',
            'level': 10,
            'icon': '👻',
            'capabilities': ['Basic viewing', 'Read-only access']
        }

        if role_result['success'] and role_result['output']:
            role_name = role_result['output'].strip()

            # Role mapping
            role_map = {
                'Ghost': {'level': 10, 'icon': '👻', 'capabilities': ['Basic viewing', 'Read-only access']},
                'Tomb': {'level': 20, 'icon': '⚰️', 'capabilities': ['Basic storage', 'Simple operations']},
                'Crypt': {'level': 30, 'icon': '🏛️', 'capabilities': ['Secure storage', 'Standard operations']},
                'Drone': {'level': 40, 'icon': '🤖', 'capabilities': ['Automation tasks', 'Maintenance']},
                'Knight': {'level': 50, 'icon': '🛡️', 'capabilities': ['Security functions', 'Standard operations']},
                'Imp': {'level': 60, 'icon': '😈', 'capabilities': ['Development tools', 'Automation']},
                'Sorcerer': {'level': 80, 'icon': '🧙', 'capabilities': ['Advanced admin', 'Debugging']},
                'Wizard': {'level': 100, 'icon': '🧙‍♂️', 'capabilities': ['Full access', 'Core development']}
            }

            if role_name in role_map:
                role_data.update(role_map[role_name])
                role_data['name'] = role_name

        return role_data

    def get_stories(self) -> List[Dict[str, Any]]:
        """Get available story templates"""
        stories_result = self.execute_command("[STORY|LIST]")

        stories = []
        if stories_result['success']:
            # Parse story output (simplified for now)
            stories = [
                {
                    'name': 'startup',
                    'title': 'System Startup Story',
                    'role': 'All',
                    'level': 10
                },
                {
                    'name': 'project-init',
                    'title': 'Project Initialization',
                    'role': 'Knight+',
                    'level': 50
                },
                {
                    'name': 'dev-setup',
                    'title': 'Development Environment',
                    'role': 'Wizard',
                    'level': 100
                }
            ]

        return stories

# Convenience functions for direct use
def get_udos_variables() -> Dict[str, str]:
    """Quick function to get all variables"""
    uv = UDOSVariables()
    return uv.list_variables()

def execute_udos_command(command: str) -> Dict[str, Any]:
    """Quick function to execute command"""
    uv = UDOSVariables()
    return uv.execute_command(command)

def get_udos_status() -> Dict[str, Any]:
    """Quick function to get system status"""
    uv = UDOSVariables()
    return {
        'system': uv.get_system_status(),
        'role': uv.get_role_info(),
        'variables': uv.list_variables(),
        'stories': uv.get_stories()
    }

if __name__ == "__main__":
    # Test the library
    uv = UDOSVariables()

    print("uDOS Variables Library Test")
    print("=" * 30)

    # Test system status
    status = uv.get_system_status()
    print(f"Router Status: {status['router_status']}")
    print(f"Variable Count: {status['variable_count']}")

    # Test role info
    role = uv.get_role_info()
    print(f"Current Role: {role['name']} (Level {role['level']})")

    # Test variables
    variables = uv.list_variables()
    print(f"Variables: {len(variables)} found")
    for name, value in list(variables.items())[:3]:  # Show first 3
        print(f"  ${name} = {value}")

    print("\nLibrary test complete")
