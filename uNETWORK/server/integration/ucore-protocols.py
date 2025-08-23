#!/usr/bin/env python3
"""
uNETWORK-uCORE Integration v1.3.3
Provides compatibility layer for uCORE logging, error handling, backup protocols,
and role-based permissions integration
"""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List

class uCOREProtocols:
    """Integration layer for uCORE logging, error, and backup protocols"""

    def __init__(self, udos_root: Path):
        self.udos_root = Path(udos_root)
        self.ucore_path = self.udos_root / "uCORE"
        self.umemory_path = self.udos_root / "uMEMORY"
        self.sandbox_path = self.udos_root / "sandbox"

        # Initialize protocol systems
        self.init_logging_protocol()
        self.init_error_protocol()
        self.init_backup_protocol()
        self.init_role_system()

    def init_logging_protocol(self):
        """Initialize uCORE logging protocol integration"""
        self.logging_config = {
            'log_dir': self.udos_root / "wizard" / "logs",
            'error_log_dir': self.udos_root / "wizard" / "logs" / "errors",
            'debug_log_dir': self.udos_root / "wizard" / "logs" / "debug",
            'crash_log_dir': self.udos_root / "wizard" / "logs" / "crashes",
            'network_log_dir': self.udos_root / "wizard" / "logs" / "network"
        }

        # Ensure log directories exist
        for log_dir in self.logging_config.values():
            log_dir.mkdir(parents=True, exist_ok=True)

        # Configure network-specific logging
        self.setup_network_logging()

    def setup_network_logging(self):
        """Setup network-specific logging with uCORE protocol compliance"""
        network_logger = logging.getLogger('uNETWORK')
        network_logger.setLevel(logging.INFO)

        # File handler for network logs
        network_log_file = self.logging_config['network_log_dir'] / f"network-{time.strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(network_log_file)
        file_handler.setLevel(logging.INFO)

        # Format compatible with uCORE error handler
        formatter = logging.Formatter(
            '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
        )
        file_handler.setFormatter(formatter)
        network_logger.addHandler(file_handler)

        self.network_logger = network_logger

    def init_error_protocol(self):
        """Initialize uCORE error protocol integration"""
        self.error_handler_path = self.ucore_path / "system" / "error-handler.sh"
        self.error_config = {
            'max_errors': 10,
            'error_threshold': 5,
            'loop_threshold': 3,
            'restart_count': 0,
            'error_count': 0
        }

    def init_backup_protocol(self):
        """Initialize uCORE backup protocol integration"""
        self.backup_config = {
            'backup_dir': self.udos_root / "backup",
            'network_backup_dir': self.udos_root / "backup" / "network",
            'auto_backup': True,
            'backup_on_error': True,
            'backup_retention': 30  # days
        }

        # Ensure backup directories exist
        for backup_dir in [self.backup_config['backup_dir'], self.backup_config['network_backup_dir']]:
            backup_dir.mkdir(parents=True, exist_ok=True)

    def init_role_system(self):
        """Initialize role-based permission system"""
        self.load_role_permissions()
        self.current_role = self.get_current_role()

    def load_role_permissions(self):
        """Load role permissions from uMEMORY/system"""
        role_file = self.umemory_path / "system" / "uDATA-user-roles.json"

        if role_file.exists():
            with open(role_file, 'r') as f:
                content = f.read().strip()
                # Parse uDATA format (one JSON object per line)
                self.role_permissions = {}
                for line in content.split('\n'):
                    if line.strip():
                        role_data = json.loads(line)
                        self.role_permissions[role_data['role']] = role_data
        else:
            # Fallback role permissions
            self.role_permissions = self.get_default_role_permissions()

    def get_default_role_permissions(self) -> Dict[str, Any]:
        """Get default role permissions if uMEMORY file not found"""
        return {
            'wizard': {'level': 100, 'permissions': {'admin': True, 'network': True, 'uScript': True}},
            'sorcerer': {'level': 75, 'permissions': {'admin': False, 'network': True, 'uScript': True}},
            'imp': {'level': 50, 'permissions': {'admin': False, 'network': True, 'uScript': 'limited'}},
            'drone': {'level': 25, 'permissions': {'admin': False, 'network': 'limited', 'uScript': 'read_only'}},
            'ghost': {'level': 10, 'permissions': {'admin': False, 'network': 'read_only', 'uScript': 'none'}}
        }

    def get_current_role(self) -> str:
        """Get current user role from sandbox configuration"""
        try:
            role_conf = self.sandbox_path / "current-role.conf"
            if role_conf.exists():
                with open(role_conf, 'r') as f:
                    for line in f:
                        if line.startswith('CURRENT_ROLE='):
                            return line.split('=')[1].strip()
            return 'wizard'  # Default role
        except Exception as e:
            self.log_error('ROLE_DETECTION', f'Failed to detect current role: {e}')
            return 'wizard'

    def check_permission(self, action: str, resource: str = None) -> bool:
        """Check if current role has permission for action"""
        try:
            role_data = self.role_permissions.get(self.current_role, {})
            permissions = role_data.get('permissions', {})

            # Check specific action permissions
            if action in permissions:
                permission = permissions[action]
                if isinstance(permission, bool):
                    return permission
                elif permission in ['full', 'read_write', True]:
                    return True
                elif permission in ['limited', 'read_only']:
                    return action in ['read', 'status', 'info']
                elif permission in ['none', False]:
                    return False

            # Check general network permissions
            if action.startswith('network'):
                network_perm = permissions.get('network', False)
                if network_perm == 'read_only' and action in ['network_read', 'network_status']:
                    return True
                return network_perm in [True, 'full', 'read_write']

            # Check uScript permissions
            if action.startswith('uscript'):
                uscript_perm = permissions.get('uScript', False)
                if uscript_perm == 'read_only' and action in ['uscript_read', 'uscript_list']:
                    return True
                return uscript_perm in [True, 'full', 'read_write']

            # Admin actions require admin permission
            if action in ['restart', 'shutdown', 'config_write', 'user_management']:
                return permissions.get('admin', False)

            # Default to allowing read operations for all roles
            return action in ['read', 'status', 'info', 'list']

        except Exception as e:
            self.log_error('PERMISSION_CHECK', f'Permission check failed for {action}: {e}')
            return False

    def log_error(self, error_type: str, message: str, exception: Exception = None) -> str:
        """Log error using uCORE error protocol"""
        try:
            error_id = self.generate_error_id()
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

            # Log to uCORE error system
            error_log_file = self.logging_config['error_log_dir'] / f"error-{time.strftime('%Y%m%d')}.log"

            with open(error_log_file, 'a') as f:
                f.write(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n")
                f.write(f"ERROR: {error_id}\\n")
                f.write(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n")
                f.write(f"Timestamp: {timestamp}\\n")
                f.write(f"Type: {error_type}\\n")
                f.write(f"Source: uNETWORK\\n")
                f.write(f"Role: {self.current_role}\\n")
                f.write(f"Message: {message}\\n")
                if exception:
                    f.write(f"Exception: {str(exception)}\\n")
                f.write(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n\\n")

            # Also log to network logger
            self.network_logger.error(f"[{error_id}] {error_type}: {message}")

            # Increment error count
            self.error_config['error_count'] += 1

            # Trigger backup if configured
            if self.backup_config['backup_on_error']:
                self.create_error_backup(error_id, error_type)

            return error_id

        except Exception as e:
            # Fallback logging if uCORE system fails
            print(f"CRITICAL: uCORE error logging failed: {e}")
            return "ERR_UNKNOWN"

    def generate_error_id(self) -> str:
        """Generate unique error ID compatible with uCORE format"""
        import random
        return f"NET{time.strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999):04x}"

    def create_error_backup(self, error_id: str, error_type: str):
        """Create backup when error occurs"""
        try:
            backup_timestamp = time.strftime('%Y%m%d-%H%M%S')
            backup_file = self.backup_config['network_backup_dir'] / f"error-backup-{backup_timestamp}-{error_id}.tar.gz"

            # Create backup of critical network files
            network_files = [
                self.udos_root / "uNETWORK" / "server" / "config",
                self.udos_root / "uNETWORK" / "server" / "server.py",
                self.logging_config['network_log_dir']
            ]

            # Use tar to create backup
            cmd = ['tar', '-czf', str(backup_file)]
            for file_path in network_files:
                if file_path.exists():
                    cmd.append(str(file_path))

            subprocess.run(cmd, check=True, capture_output=True)

            self.network_logger.info(f"Error backup created: {backup_file}")

        except Exception as e:
            self.network_logger.error(f"Failed to create error backup: {e}")

    def integrate_with_uscript(self) -> bool:
        """Integrate with uSCRIPT virtual environment and execution system"""
        try:
            uscript_path = self.udos_root / "uSCRIPT"
            venv_path = uscript_path / "venv" / "python"

            # Check if uSCRIPT is available
            if not uscript_path.exists():
                self.log_error('USCRIPT_INTEGRATION', 'uSCRIPT directory not found')
                return False

            # Check virtual environment
            if venv_path.exists():
                # Test virtual environment activation
                activate_script = venv_path / "bin" / "activate"
                if activate_script.exists():
                    self.network_logger.info("uSCRIPT virtual environment integration successful")
                    return True
                else:
                    self.log_error('USCRIPT_VENV', 'uSCRIPT virtual environment not properly configured')
                    return False
            else:
                self.network_logger.warning("uSCRIPT virtual environment not found - will use system Python")
                return True

        except Exception as e:
            self.log_error('USCRIPT_INTEGRATION', f'Failed to integrate with uSCRIPT: {e}', e)
            return False

    def execute_uscript(self, script_name: str, args: List[str] = None) -> Dict[str, Any]:
        """Execute uSCRIPT with proper role permissions and error handling"""
        try:
            # Check permissions first
            if not self.check_permission('uscript_execute'):
                return {
                    'success': False,
                    'error': 'Permission denied: Current role cannot execute uSCRIPT',
                    'role': self.current_role
                }

            uscript_main = self.udos_root / "uSCRIPT" / "uscript.sh"
            if not uscript_main.exists():
                return {
                    'success': False,
                    'error': 'uSCRIPT not found',
                    'path': str(uscript_main)
                }

            # Build command
            cmd = [str(uscript_main), 'run', script_name]
            if args:
                cmd.extend(args)

            # Set environment variables for role context
            env = os.environ.copy()
            env['UDOS_CURRENT_ROLE'] = self.current_role
            env['UDOS_NETWORK_CONTEXT'] = 'true'

            # Execute with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env=env
            )

            if result.returncode == 0:
                self.network_logger.info(f"uSCRIPT execution successful: {script_name}")
                return {
                    'success': True,
                    'output': result.stdout,
                    'script': script_name,
                    'role': self.current_role
                }
            else:
                error_id = self.log_error('USCRIPT_EXECUTION', f'uSCRIPT failed: {script_name}')
                return {
                    'success': False,
                    'error': result.stderr or 'Unknown error',
                    'error_id': error_id,
                    'script': script_name
                }

        except subprocess.TimeoutExpired:
            error_id = self.log_error('USCRIPT_TIMEOUT', f'uSCRIPT timeout: {script_name}')
            return {
                'success': False,
                'error': 'Script execution timeout',
                'error_id': error_id,
                'script': script_name
            }
        except Exception as e:
            error_id = self.log_error('USCRIPT_ERROR', f'uSCRIPT execution error: {e}', e)
            return {
                'success': False,
                'error': str(e),
                'error_id': error_id,
                'script': script_name
            }

    def access_umemory_resource(self, resource_path: str, operation: str = 'read') -> Optional[Any]:
        """Access uMEMORY resources with role-based permissions"""
        try:
            # Check permissions
            if not self.check_permission(f'umemory_{operation}'):
                self.log_error('UMEMORY_ACCESS', f'Permission denied for {operation} on {resource_path}')
                return None

            full_path = self.umemory_path / resource_path

            if not full_path.exists():
                self.log_error('UMEMORY_ACCESS', f'Resource not found: {resource_path}')
                return None

            if operation == 'read':
                if full_path.suffix == '.json':
                    with open(full_path, 'r') as f:
                        return json.load(f)
                else:
                    with open(full_path, 'r') as f:
                        return f.read()
            elif operation == 'write':
                # Writing requires higher permissions
                if not self.check_permission('umemory_write'):
                    self.log_error('UMEMORY_ACCESS', f'Write permission denied for {resource_path}')
                    return None
                # Writing implementation would go here
                return True

        except Exception as e:
            self.log_error('UMEMORY_ACCESS', f'Failed to access {resource_path}: {e}', e)
            return None

    def use_sandbox(self, operation: str, path: str = None) -> Optional[Path]:
        """Use sandbox with role-based restrictions"""
        try:
            role_data = self.role_permissions.get(self.current_role, {})
            folder_access = role_data.get('folder_access', {})
            sandbox_access = folder_access.get('sandbox', 'none')

            if sandbox_access == 'none':
                self.log_error('SANDBOX_ACCESS', f'Sandbox access denied for role {self.current_role}')
                return None

            if sandbox_access == 'demo_only':
                sandbox_path = self.sandbox_path / "demos"
            elif sandbox_access == 'read_write_limited':
                sandbox_path = self.sandbox_path / "user"
            else:  # full access
                sandbox_path = self.sandbox_path

            if path:
                sandbox_path = sandbox_path / path

            # Ensure path exists for write operations
            if operation in ['write', 'create'] and not sandbox_path.exists():
                sandbox_path.mkdir(parents=True, exist_ok=True)

            self.network_logger.info(f"Sandbox access granted: {sandbox_path}")
            return sandbox_path

        except Exception as e:
            self.log_error('SANDBOX_ACCESS', f'Sandbox access error: {e}', e)
            return None

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including all protocol integrations"""
        try:
            status = {
                'ucore_integration': {
                    'logging': self.logging_config['log_dir'].exists(),
                    'error_handler': self.error_handler_path.exists(),
                    'backup_system': self.backup_config['backup_dir'].exists()
                },
                'role_system': {
                    'current_role': self.current_role,
                    'role_level': self.role_permissions.get(self.current_role, {}).get('level', 0),
                    'permissions_loaded': len(self.role_permissions) > 0
                },
                'uscript_integration': {
                    'available': (self.udos_root / "uSCRIPT").exists(),
                    'venv_active': (self.udos_root / "uSCRIPT" / "venv" / "python").exists()
                },
                'umemory_integration': {
                    'available': self.umemory_path.exists(),
                    'system_resources': (self.umemory_path / "system").exists()
                },
                'sandbox_integration': {
                    'available': self.sandbox_path.exists(),
                    'current_role_access': self.check_permission('sandbox')
                },
                'error_stats': {
                    'error_count': self.error_config['error_count'],
                    'restart_count': self.error_config['restart_count']
                }
            }

            return status

        except Exception as e:
            self.log_error('STATUS_ERROR', f'Failed to get system status: {e}', e)
            return {'error': 'Status unavailable'}


def create_ucore_integration(udos_root: str) -> uCOREProtocols:
    """Factory function to create uCORE integration instance"""
    return uCOREProtocols(Path(udos_root))


# Test integration if run directly
if __name__ == "__main__":
    udos_root = Path(__file__).parent.parent.parent
    protocols = create_ucore_integration(udos_root)

    print("uNETWORK-uCORE Integration Test")
    print("=" * 40)

    status = protocols.get_system_status()
    for category, details in status.items():
        print(f"\n{category}:")
        for key, value in details.items():
            print(f"  {key}: {value}")

    print(f"\nCurrent role: {protocols.current_role}")
    print(f"Network permission: {protocols.check_permission('network')}")
    print(f"uScript permission: {protocols.check_permission('uscript_execute')}")
    print(f"Admin permission: {protocols.check_permission('admin')}")
