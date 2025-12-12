"""
Role-Based Permissions System

Manages user roles (viewer/user/contributor/admin/wizard) with password
authentication and wizard auto-detection from git authors.

Part of v1.2.22 - Self-Healing & Auto-Error-Awareness System
"""

import json
import os
import re
import subprocess
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    import hashlib

from core.config import Config


class UserRole(Enum):
    """User role levels with increasing permissions."""
    VIEWER = "viewer"          # Read-only access
    USER = "user"              # Basic commands, memory/ access
    CONTRIBUTOR = "contributor"  # Can submit content, create workflows
    ADMIN = "admin"            # Full system access with password
    WIZARD = "wizard"          # Maintainer access, auto-detected


class RoleManager:
    """Manages user roles and permissions."""
    
    def __init__(self, config: Config):
        self.config = config
        self.profile_path = Path(config.workspace_root) / "memory" / "bank" / "user" / "profile.json"
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._current_role = None
        self._load_profile()
    
    def _load_profile(self):
        """Load user profile with role information."""
        if self.profile_path.exists():
            try:
                with open(self.profile_path, 'r') as f:
                    profile = json.load(f)
                    role_str = profile.get('role', 'user')
                    self._current_role = UserRole(role_str)
            except Exception:
                self._current_role = UserRole.USER
        else:
            # Default to user, check if wizard
            self._current_role = UserRole.USER
            if self._detect_wizard():
                self._current_role = UserRole.WIZARD
            self._save_profile()
    
    def _save_profile(self):
        """Save user profile."""
        profile = {
            'role': self._current_role.value,
            'wizard_detected': self._detect_wizard()
        }
        
        with open(self.profile_path, 'w') as f:
            json.dump(profile, f, indent=2)
    
    def _detect_wizard(self) -> bool:
        """Auto-detect wizard role from git author matching CREDITS.md."""
        try:
            # Get git user email
            result = subprocess.run(
                ['git', 'config', 'user.email'],
                capture_output=True,
                text=True,
                timeout=2,
                cwd=self.config.workspace_root
            )
            
            if result.returncode != 0:
                # Try getting from last commit
                result = subprocess.run(
                    ['git', 'log', '--format=%ae', '-n', '1'],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    cwd=self.config.workspace_root
                )
            
            if result.returncode != 0:
                return False
            
            git_email = result.stdout.strip().lower()
            if not git_email:
                return False
            
            # Parse CREDITS.md for maintainer emails
            credits_path = Path(self.config.workspace_root) / "CREDITS.md"
            if not credits_path.exists():
                return False
            
            with open(credits_path, 'r') as f:
                content = f.read()
            
            # Extract emails from CREDITS.md
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)
            maintainer_emails = [e.lower() for e in emails]
            
            return git_email in maintainer_emails
            
        except Exception:
            return False
    
    def get_current_role(self) -> UserRole:
        """Get current user role."""
        return self._current_role
    
    def set_role(self, role: UserRole, password: Optional[str] = None) -> bool:
        """Set user role (requires password for admin/wizard)."""
        # Wizard role requires git author match
        if role == UserRole.WIZARD:
            if not self._detect_wizard():
                return False
        
        # Admin role requires password
        if role == UserRole.ADMIN:
            if not password or not self.verify_password(password):
                return False
        
        self._current_role = role
        self._save_profile()
        return True
    
    def check_permission(self, action: str, required_role: Optional[UserRole] = None) -> bool:
        """Check if current role has permission for action."""
        current_level = list(UserRole).index(self._current_role)
        
        # Define action requirements
        action_requirements = {
            'read_knowledge': UserRole.VIEWER,
            'write_memory': UserRole.USER,
            'run_workflows': UserRole.USER,
            'submit_content': UserRole.CONTRIBUTOR,
            'edit_core': UserRole.ADMIN,
            'edit_extensions': UserRole.ADMIN,
            'dev_mode': UserRole.ADMIN,
            'sandbox_test': UserRole.ADMIN,
            'pattern_clear': UserRole.ADMIN,
        }
        
        if required_role:
            required_level = list(UserRole).index(required_role)
        elif action in action_requirements:
            required_level = list(UserRole).index(action_requirements[action])
        else:
            # Unknown action, require user level
            required_level = list(UserRole).index(UserRole.USER)
        
        return current_level >= required_level
    
    def verify_password(self, input_password: str) -> bool:
        """Verify password against stored hash."""
        stored_hash = self.config.get_env('USER_PASSWORD_HASH')
        
        if not stored_hash:
            # No password set, check plain text (for initial setup)
            plain_password = self.config.get_env('USER_PASSWORD', '')
            if plain_password:
                # Migrate to hashed
                self.set_password(plain_password)
                return input_password == plain_password
            # No password required
            return True
        
        if BCRYPT_AVAILABLE:
            try:
                return bcrypt.checkpw(input_password.encode(), stored_hash.encode())
            except Exception:
                return False
        else:
            # Fallback to SHA256 (less secure)
            input_hash = hashlib.sha256(input_password.encode()).hexdigest()
            return input_hash == stored_hash
    
    def set_password(self, password: str) -> bool:
        """Set/update password (minimum 4 characters)."""
        if len(password) < 4 and password:  # Allow empty password
            return False
        
        if not password:
            # Remove password
            self.config.set_env('USER_PASSWORD_HASH', '')
            self.config.set_env('USER_PASSWORD', '')
            return True
        
        if BCRYPT_AVAILABLE:
            # Use bcrypt with cost factor 12
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
            self.config.set_env('USER_PASSWORD_HASH', hashed.decode())
            # Clear plain text password
            self.config.set_env('USER_PASSWORD', '')
        else:
            # Fallback to SHA256
            hashed = hashlib.sha256(password.encode()).hexdigest()
            self.config.set_env('USER_PASSWORD_HASH', hashed)
            self.config.set_env('USER_PASSWORD', '')
        
        return True
    
    def prompt_password(self, prompt: str = "Enter password: ", max_attempts: int = 3) -> Optional[str]:
        """Prompt for password with hidden input."""
        import getpass
        
        for attempt in range(max_attempts):
            try:
                password = getpass.getpass(prompt)
                if self.verify_password(password):
                    return password
                else:
                    if attempt < max_attempts - 1:
                        print(f"❌ Incorrect password. {max_attempts - attempt - 1} attempts remaining.")
            except (EOFError, KeyboardInterrupt):
                return None
        
        print("❌ Maximum attempts exceeded. Access denied.")
        return None
    
    def get_role_info(self) -> dict:
        """Get current role information."""
        return {
            'role': self._current_role.value,
            'role_name': self._current_role.name,
            'wizard_detected': self._detect_wizard(),
            'permissions': {
                'read_knowledge': self.check_permission('read_knowledge'),
                'write_memory': self.check_permission('write_memory'),
                'run_workflows': self.check_permission('run_workflows'),
                'submit_content': self.check_permission('submit_content'),
                'edit_core': self.check_permission('edit_core'),
                'edit_extensions': self.check_permission('edit_extensions'),
                'dev_mode': self.check_permission('dev_mode'),
                'sandbox_test': self.check_permission('sandbox_test'),
            }
        }
    
    def get_debug_info(self) -> dict:
        """Get debug information for wizard detection."""
        info = {
            'current_role': self._current_role.value,
            'wizard_detected': False,
            'git_author': None,
            'credits_emails': [],
            'match_found': False
        }
        
        try:
            # Get git author
            result = subprocess.run(
                ['git', 'config', 'user.email'],
                capture_output=True,
                text=True,
                timeout=2,
                cwd=self.config.workspace_root
            )
            if result.returncode == 0:
                info['git_author'] = result.stdout.strip()
            
            # Get CREDITS emails
            credits_path = Path(self.config.workspace_root) / "CREDITS.md"
            if credits_path.exists():
                with open(credits_path, 'r') as f:
                    content = f.read()
                info['credits_emails'] = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)
            
            # Check match
            if info['git_author']:
                git_email = info['git_author'].lower()
                credits_emails = [e.lower() for e in info['credits_emails']]
                info['match_found'] = git_email in credits_emails
                info['wizard_detected'] = info['match_found']
        
        except Exception as e:
            info['error'] = str(e)
        
        return info
