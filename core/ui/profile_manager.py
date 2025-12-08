"""
Profile Manager (v1.2.18)

Save and load configuration profiles for quick workspace switching.
Import/export settings as JSON.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime
from core.config import Config


class ProfileManager:
    """
    Manage configuration profiles.
    
    Features:
    - Save current config as profile
    - Load config from profile
    - Quick workspace switching
    - Import/export JSON
    - Default profile management
    """
    
    def __init__(self):
        """Initialize profile manager"""
        self.config = Config()
        
        # Profiles storage
        from core.utils.paths import PATHS
        self.profiles_dir = PATHS.MEMORY_SYSTEM_USER / "profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Load available profiles
        self.profiles = self._load_profiles()
        
        # UI state
        self.selected_index = 0
        self.creating_profile = False
        self.profile_name_buffer = ''
        
    def _load_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load all available profiles"""
        profiles = {}
        
        for profile_file in self.profiles_dir.glob('*.json'):
            try:
                with open(profile_file, 'r') as f:
                    profile_data = json.load(f)
                    profiles[profile_file.stem] = profile_data
            except Exception:
                pass
        
        return profiles
    
    def render(self) -> str:
        """Render profile manager panel"""
        output = []
        
        # Header
        output.append("╔══ PROFILE MANAGER ══╗")
        output.append("")
        
        # Info
        output.append(f"Profiles Directory: {self.profiles_dir}")
        output.append("=" * 70)
        output.append("")
        
        # Creating new profile
        if self.creating_profile:
            output.append("Creating New Profile:")
            output.append(f"  Name: [{self.profile_name_buffer}]_")
            output.append("")
            output.append("[ENTER] Create  [ESC] Cancel")
            return "\n".join(output)
        
        # Profiles list
        output.extend(self._render_profiles())
        
        # Footer
        output.append("")
        output.append(self._render_footer())
        
        return "\n".join(output)
    
    def _render_profiles(self) -> List[str]:
        """Render profiles list"""
        output = []
        
        if not self.profiles:
            output.append("  (No profiles saved)")
            output.append("")
            output.append("  Press [N] to create your first profile")
            return output
        
        # Sort profiles by name
        sorted_names = sorted(self.profiles.keys())
        
        # Render each profile
        for i, name in enumerate(sorted_names):
            profile = self.profiles[name]
            
            # Highlight selected
            prefix = "→ " if i == self.selected_index else "  "
            
            # Default indicator
            is_default = profile.get('is_default', False)
            default_mark = " [DEFAULT]" if is_default else ""
            
            # Name and timestamp
            created = profile.get('created', 'unknown')
            output.append(f"{prefix}{name}{default_mark}")
            output.append(f"     Created: {created}")
            
            # Description if available
            desc = profile.get('description', '')
            if desc:
                output.append(f"     {desc}")
            
            # Settings count
            settings_count = len(profile.get('settings', {}))
            output.append(f"     {settings_count} settings")
            output.append("")
        
        return output
    
    def _render_footer(self) -> str:
        """Render footer with controls"""
        controls = [
            "↑↓ Navigate",
            "[L]oad",
            "[N]ew Profile",
            "[D]elete",
            "[E]xport",
            "[I]mport",
            "[ESC] Back"
        ]
        return "  ".join(controls)
    
    def move_selection(self, delta: int):
        """Move selection up/down"""
        sorted_names = sorted(self.profiles.keys())
        if not sorted_names:
            return
        
        self.selected_index = (self.selected_index + delta) % len(sorted_names)
    
    def start_create_profile(self):
        """Start creating a new profile"""
        self.creating_profile = True
        self.profile_name_buffer = ''
    
    def update_profile_name_buffer(self, char: str):
        """Update profile name buffer"""
        if char == '\x7f':  # Backspace
            self.profile_name_buffer = self.profile_name_buffer[:-1]
        elif char.isprintable() and char not in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
            # Only allow valid filename characters
            self.profile_name_buffer += char
    
    def cancel_create_profile(self):
        """Cancel profile creation"""
        self.creating_profile = False
        self.profile_name_buffer = ''
    
    def save_current_as_profile(self, name: str, description: str = '') -> Dict[str, Any]:
        """Save current configuration as a profile"""
        if not name:
            return {'success': False, 'error': 'Profile name required'}
        
        # Sanitize name
        name = name.strip()
        if not name:
            return {'success': False, 'error': 'Profile name cannot be empty'}
        
        # Get all current settings
        settings = {}
        for key in self.config._config:
            settings[key] = self.config.get(key)
        
        # Create profile data
        profile_data = {
            'name': name,
            'description': description,
            'created': datetime.now().isoformat(),
            'settings': settings,
            'is_default': False
        }
        
        # Save to file
        profile_file = self.profiles_dir / f"{name}.json"
        try:
            with open(profile_file, 'w') as f:
                json.dump(profile_data, f, indent=2)
            
            # Add to profiles
            self.profiles[name] = profile_data
            
            return {'success': True, 'name': name, 'file': str(profile_file)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def load_profile(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Load a profile"""
        # Use selected profile if no name provided
        if name is None:
            sorted_names = sorted(self.profiles.keys())
            if not sorted_names or self.selected_index >= len(sorted_names):
                return {'success': False, 'error': 'No profile selected'}
            name = sorted_names[self.selected_index]
        
        # Check if profile exists
        if name not in self.profiles:
            return {'success': False, 'error': f'Profile not found: {name}'}
        
        # Load settings
        profile = self.profiles[name]
        settings = profile.get('settings', {})
        
        # Apply settings to config
        try:
            for key, value in settings.items():
                self.config.set(key, value)
            
            self.config.save()
            
            return {'success': True, 'name': name, 'settings_count': len(settings)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_profile(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Delete a profile"""
        # Use selected profile if no name provided
        if name is None:
            sorted_names = sorted(self.profiles.keys())
            if not sorted_names or self.selected_index >= len(sorted_names):
                return {'success': False, 'error': 'No profile selected'}
            name = sorted_names[self.selected_index]
        
        # Check if profile exists
        if name not in self.profiles:
            return {'success': False, 'error': f'Profile not found: {name}'}
        
        # Delete file
        profile_file = self.profiles_dir / f"{name}.json"
        try:
            profile_file.unlink()
            del self.profiles[name]
            
            # Adjust selection
            if self.selected_index >= len(self.profiles):
                self.selected_index = max(0, len(self.profiles) - 1)
            
            return {'success': True, 'name': name}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def set_default_profile(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Set a profile as default"""
        # Use selected profile if no name provided
        if name is None:
            sorted_names = sorted(self.profiles.keys())
            if not sorted_names or self.selected_index >= len(sorted_names):
                return {'success': False, 'error': 'No profile selected'}
            name = sorted_names[self.selected_index]
        
        # Check if profile exists
        if name not in self.profiles:
            return {'success': False, 'error': f'Profile not found: {name}'}
        
        # Clear other defaults
        for profile_name in self.profiles:
            self.profiles[profile_name]['is_default'] = False
        
        # Set new default
        self.profiles[name]['is_default'] = True
        
        # Save all profiles
        for profile_name, profile_data in self.profiles.items():
            profile_file = self.profiles_dir / f"{profile_name}.json"
            try:
                with open(profile_file, 'w') as f:
                    json.dump(profile_data, f, indent=2)
            except Exception:
                pass
        
        return {'success': True, 'name': name}
    
    def export_profile(self, name: Optional[str] = None, export_path: Optional[Path] = None) -> Dict[str, Any]:
        """Export a profile to JSON file"""
        # Use selected profile if no name provided
        if name is None:
            sorted_names = sorted(self.profiles.keys())
            if not sorted_names or self.selected_index >= len(sorted_names):
                return {'success': False, 'error': 'No profile selected'}
            name = sorted_names[self.selected_index]
        
        # Check if profile exists
        if name not in self.profiles:
            return {'success': False, 'error': f'Profile not found: {name}'}
        
        # Default export path
        if export_path is None:
            from core.utils.paths import PATHS
            export_path = PATHS.MEMORY_DOCS / f"profile_{name}.json"
        
        # Export
        try:
            with open(export_path, 'w') as f:
                json.dump(self.profiles[name], f, indent=2)
            
            return {'success': True, 'name': name, 'file': str(export_path)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def import_profile(self, import_path: Path) -> Dict[str, Any]:
        """Import a profile from JSON file"""
        if not import_path.exists():
            return {'success': False, 'error': f'File not found: {import_path}'}
        
        try:
            with open(import_path, 'r') as f:
                profile_data = json.load(f)
            
            # Validate profile data
            if 'name' not in profile_data:
                return {'success': False, 'error': 'Invalid profile: missing name'}
            if 'settings' not in profile_data:
                return {'success': False, 'error': 'Invalid profile: missing settings'}
            
            name = profile_data['name']
            
            # Save to profiles directory
            result = self.save_current_as_profile(
                name=name,
                description=profile_data.get('description', '')
            )
            
            if result['success']:
                # Update with imported settings
                self.profiles[name] = profile_data
                profile_file = self.profiles_dir / f"{name}.json"
                with open(profile_file, 'w') as f:
                    json.dump(profile_data, f, indent=2)
            
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get manager summary"""
        default_profile = None
        for name, profile in self.profiles.items():
            if profile.get('is_default'):
                default_profile = name
                break
        
        return {
            'total_profiles': len(self.profiles),
            'default_profile': default_profile,
            'profiles_dir': str(self.profiles_dir),
            'creating': self.creating_profile
        }


# Global instance
_profile_manager: Optional[ProfileManager] = None


def get_profile_manager() -> ProfileManager:
    """Get global ProfileManager instance"""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = ProfileManager()
    return _profile_manager
