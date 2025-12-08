"""
Config Initializer for uDOS v1.2.15

Modernizes configuration system using v1.2.x standards:
- Schema v1.2.15 with strict validation
- PATHS constants throughout (no hardcoded paths)
- Interactive wizard for first-run setup
- Auto-detect missing folders and prompt user
- Backup existing configs to .archive/ before changes

Usage:
    from core.services.config_initializer import ConfigInitializer
    
    # First-run setup
    initializer = ConfigInitializer()
    config = initializer.run_wizard()
    
    # Load existing config
    config = initializer.load_config()
    
    # Validate config
    is_valid, errors = initializer.validate_config(config)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import shutil

from core.utils.paths import PATHS


class ConfigSchema:
    """Schema definition for uDOS v1.2.15 configuration."""
    
    VERSION = "1.2.15"
    
    # Required top-level keys
    REQUIRED_KEYS = {
        "schema_version",
        "installation",
        "paths",
        "user",
        "graphics",
        "extensions",
    }
    
    # Default configuration
    DEFAULT_CONFIG = {
        "schema_version": VERSION,
        "installation": {
            "install_date": None,  # Set during initialization
            "python_version": None,  # Detected automatically
            "udos_version": VERSION,
        },
        "paths": {
            "workspace_root": None,  # Auto-detected
            "memory_root": "memory/",
            "knowledge_root": "knowledge/",
            "extensions_root": "extensions/",
        },
        "user": {
            "theme": "foundation",
            "location": "AA340",  # Sydney default
            "offline_mode": True,
        },
        "graphics": {
            "default_format": "ascii",
            "ai_enabled": False,
            "size_limits": {
                "ascii_max_kb": 5,
                "teletext_max_kb": 10,
                "svg_max_kb": 50,
                "sequence_max_kb": 5,
                "flow_max_kb": 5,
                "prompt_max_kb": 2,
            },
        },
        "extensions": {
            "graphics_renderer_port": 5555,
            "enabled_services": ["extension-manager"],
        },
    }
    
    @classmethod
    def validate(cls, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate configuration against schema.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check schema version
        if config.get("schema_version") != cls.VERSION:
            errors.append(f"Schema version mismatch: expected {cls.VERSION}, got {config.get('schema_version')}")
        
        # Check required top-level keys
        missing_keys = cls.REQUIRED_KEYS - set(config.keys())
        if missing_keys:
            errors.append(f"Missing required keys: {', '.join(missing_keys)}")
        
        # Validate installation section
        if "installation" in config:
            inst = config["installation"]
            if not inst.get("install_date"):
                errors.append("installation.install_date is required")
            if not inst.get("python_version"):
                errors.append("installation.python_version is required")
        
        # Validate paths section
        if "paths" in config:
            paths = config["paths"]
            for key in ["workspace_root", "memory_root", "knowledge_root", "extensions_root"]:
                if key not in paths:
                    errors.append(f"paths.{key} is required")
        
        # Validate graphics size limits
        if "graphics" in config and "size_limits" in config["graphics"]:
            limits = config["graphics"]["size_limits"]
            required_limits = ["ascii_max_kb", "teletext_max_kb", "svg_max_kb", 
                             "sequence_max_kb", "flow_max_kb", "prompt_max_kb"]
            for limit in required_limits:
                if limit not in limits:
                    errors.append(f"graphics.size_limits.{limit} is required")
                elif not isinstance(limits[limit], (int, float)):
                    errors.append(f"graphics.size_limits.{limit} must be a number")
        
        return (len(errors) == 0, errors)


class ConfigInitializer:
    """Initializes and manages uDOS configuration."""
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize config manager.
        
        Args:
            workspace_root: Optional custom workspace root (defaults to PATHS.WORKSPACE_ROOT)
        """
        self.workspace_root = workspace_root or PATHS.WORKSPACE_ROOT
        self.config_file = PATHS.MEMORY_SYSTEM_USER / "config.json"
        self.archive_dir = PATHS.MEMORY_SYSTEM_USER / ".archive"
        
    def load_config(self) -> Dict[str, Any]:
        """Load existing configuration or return default.
        
        Returns:
            Configuration dictionary
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Validate loaded config
                is_valid, errors = ConfigSchema.validate(config)
                if not is_valid:
                    print(f"⚠️  Configuration validation errors:")
                    for error in errors:
                        print(f"   - {error}")
                    print(f"\nReturning default configuration. Please run wizard to fix.")
                    return self._get_default_config()
                
                return config
            except Exception as e:
                print(f"❌ Error loading config: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()
    
    def save_config(self, config: Dict[str, Any], backup: bool = True) -> bool:
        """Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
            backup: Whether to backup existing config first
            
        Returns:
            True if successful, False otherwise
        """
        # Validate before saving
        is_valid, errors = ConfigSchema.validate(config)
        if not is_valid:
            print(f"❌ Cannot save invalid configuration:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        # Backup existing config
        if backup and self.config_file.exists():
            self._backup_config()
        
        # Ensure directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write config
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Configuration saved to: {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False
    
    def run_wizard(self, interactive: bool = True) -> Dict[str, Any]:
        """Run interactive setup wizard.
        
        Args:
            interactive: If False, use defaults without prompting
            
        Returns:
            Configured dictionary
        """
        print("╔══════════════════════════════════════════════════════════╗")
        print("║         uDOS v1.2.15 Configuration Wizard               ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        
        config = self._get_default_config()
        
        if interactive:
            # User preferences
            print("📍 User Preferences")
            print()
            
            theme = self._prompt("Theme", config["user"]["theme"], 
                               ["foundation", "galaxy", "minimal"])
            config["user"]["theme"] = theme
            
            location = self._prompt("Default location (TILE code)", 
                                  config["user"]["location"])
            config["user"]["location"] = location
            
            offline_mode = self._prompt_bool("Offline mode (recommended)", 
                                           config["user"]["offline_mode"])
            config["user"]["offline_mode"] = offline_mode
            
            # Graphics settings
            print()
            print("🎨 Graphics Settings")
            print()
            
            default_format = self._prompt("Default graphics format", 
                                        config["graphics"]["default_format"],
                                        ["ascii", "teletext", "svg", "sequence", "flow"])
            config["graphics"]["default_format"] = default_format
            
            if default_format == "svg":
                ai_enabled = self._prompt_bool("Enable AI-assisted SVG generation", 
                                             config["graphics"]["ai_enabled"])
                config["graphics"]["ai_enabled"] = ai_enabled
        
        # Detect missing folders
        print()
        print("🔍 Checking folder structure...")
        missing_folders = self._check_folder_structure()
        
        if missing_folders:
            print(f"\n⚠️  Missing {len(missing_folders)} required folders:")
            for folder in missing_folders:
                print(f"   - {folder}")
            
            if interactive:
                create = self._prompt_bool("\nCreate missing folders?", True)
                if create:
                    self._create_missing_folders(missing_folders)
            else:
                self._create_missing_folders(missing_folders)
        else:
            print("✅ All required folders present")
        
        # Save configuration
        print()
        if interactive:
            save = self._prompt_bool("Save configuration?", True)
            if save:
                self.save_config(config, backup=True)
        else:
            self.save_config(config, backup=True)
        
        print()
        print("✅ Configuration wizard complete!")
        print()
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration with runtime values."""
        config = ConfigSchema.DEFAULT_CONFIG.copy()
        
        # Set runtime values
        config["installation"]["install_date"] = datetime.now().isoformat()
        config["installation"]["python_version"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        config["paths"]["workspace_root"] = str(self.workspace_root)
        
        return config
    
    def _backup_config(self):
        """Backup current configuration to .archive/"""
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.archive_dir / f"{timestamp}_config.json"
        
        shutil.copy2(self.config_file, backup_file)
        print(f"📦 Backed up config to: {backup_file.relative_to(self.workspace_root)}")
    
    def _check_folder_structure(self) -> List[Path]:
        """Check for missing required folders.
        
        Returns:
            List of missing folder paths
        """
        required_folders = [
            PATHS.MEMORY,
            PATHS.MEMORY_UCODE,
            PATHS.MEMORY_UCODE / "scripts",
            PATHS.MEMORY_UCODE / "tests",
            PATHS.MEMORY_UCODE / "sandbox",
            PATHS.MEMORY_UCODE / "stdlib",
            PATHS.MEMORY_UCODE / "examples",
            PATHS.MEMORY_UCODE / "adventures",
            PATHS.MEMORY_SYSTEM,
            PATHS.MEMORY_SYSTEM_USER,
            PATHS.KNOWLEDGE,
            PATHS.CORE_DATA,
            PATHS.CORE_DATA / "diagrams",
        ]
        
        missing = []
        for folder in required_folders:
            if not folder.exists():
                missing.append(folder)
        
        return missing
    
    def _create_missing_folders(self, folders: List[Path]):
        """Create missing folders with .gitkeep files."""
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)
            gitkeep = folder / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.touch()
            print(f"   ✅ Created: {folder.relative_to(self.workspace_root)}")
    
    def _prompt(self, question: str, default: Any, choices: List[str] = None) -> str:
        """Prompt user for input with default value.
        
        Args:
            question: Question to ask
            default: Default value
            choices: Optional list of valid choices
            
        Returns:
            User input or default
        """
        if choices:
            choices_str = "/".join(choices)
            prompt = f"{question} [{default}] ({choices_str}): "
        else:
            prompt = f"{question} [{default}]: "
        
        response = input(prompt).strip()
        
        if not response:
            return default
        
        if choices and response not in choices:
            print(f"⚠️  Invalid choice. Using default: {default}")
            return default
        
        return response
    
    def _prompt_bool(self, question: str, default: bool) -> bool:
        """Prompt user for yes/no input.
        
        Args:
            question: Question to ask
            default: Default value
            
        Returns:
            Boolean response
        """
        default_str = "Y/n" if default else "y/N"
        response = input(f"{question} [{default_str}]: ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', 'true', '1']
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate configuration against schema.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            (is_valid, list_of_errors)
        """
        return ConfigSchema.validate(config)


# Convenience function for first-run setup
def initialize_config(interactive: bool = True) -> Dict[str, Any]:
    """Initialize uDOS configuration.
    
    Args:
        interactive: If True, run interactive wizard
        
    Returns:
        Configuration dictionary
    """
    initializer = ConfigInitializer()
    return initializer.run_wizard(interactive=interactive)


if __name__ == '__main__':
    # Run wizard if executed directly
    initialize_config(interactive=True)
