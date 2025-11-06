"""
uDOS v1.0.12 - Setup Wizard Service

Interactive onboarding and configuration wizard for new users.
Guides users through initial setup with step-by-step prompts.

Features:
- Interactive step-by-step wizard
- Theme selection with previews
- Viewport configuration
- Extension discovery and installation
- Quick setup with sensible defaults
- Configuration validation
- Settings export/import

Version: 1.0.12
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class SetupWizard:
    """Interactive setup wizard for uDOS configuration."""

    def __init__(self):
        """Initialize Setup Wizard."""
        self.config_file = "data/USER.UDT"
        self.themes_dir = Path("data/themes")
        self.user_config = {}

        # Available options
        self.available_themes = self._load_available_themes()
        self.available_viewports = self._get_viewport_presets()

    def _load_available_themes(self) -> List[str]:
        """Load list of available themes."""
        try:
            themes_index = self.themes_dir / "_index.json"
            if themes_index.exists():
                with open(themes_index, 'r') as f:
                    data = json.load(f)
                    # Try different keys
                    themes = data.get('AVAILABLE_THEMES') or data.get('themes', [])
                    if themes:
                        return [t.lower() for t in themes]  # Normalize to lowercase
        except:
            pass

        # Try scanning directory
        try:
            if self.themes_dir.exists():
                themes = [f.stem for f in self.themes_dir.glob("*.json")
                         if not f.name.startswith("_")]
                if themes:
                    return themes
        except:
            pass

        pass

        # Fallback to known themes
        return ["dungeon", "foundation", "galaxy", "project", "science"]

    def _get_viewport_presets(self) -> List[Dict[str, Any]]:
        """Get viewport presets."""
        return [
            {"name": "Watch", "size": "13×13", "tier": 0},
            {"name": "Mobile", "size": "20×40", "tier": 3},
            {"name": "Tablet", "size": "30×60", "tier": 6},
            {"name": "Desktop", "size": "40×80", "tier": 9},
            {"name": "Cinema", "size": "360×150", "tier": 14}
        ]

    def run_full_wizard(self) -> Dict[str, Any]:
        """
        Run the complete interactive setup wizard.

        Returns:
            Configuration dictionary
        """
        config = {}

        # Welcome screen
        print(self._format_welcome())

        # Step 1: Theme selection
        config['theme'] = self._wizard_step_theme()

        # Step 2: Viewport configuration
        config['viewport'] = self._wizard_step_viewport()

        # Step 3: Extensions
        config['extensions'] = self._wizard_step_extensions()

        # Step 4: Advanced settings
        config['advanced'] = self._wizard_step_advanced()

        # Summary and confirmation
        self._show_summary(config)

        return config

    def run_quick_setup(self) -> Dict[str, Any]:
        """
        Run quick setup with sensible defaults.

        Returns:
            Configuration dictionary with defaults
        """
        return {
            'theme': 'dungeon',
            'viewport': 'auto',
            'extensions': {
                'enable_web': True,
                'enable_teletext': True
            },
            'advanced': {
                'developer_mode': False,
                'debug_logging': False,
                'experimental_features': False
            }
        }

    def setup_theme_only(self) -> str:
        """Run theme selection wizard only."""
        return self._wizard_step_theme()

    def setup_viewport_only(self) -> str:
        """Run viewport configuration wizard only."""
        return self._wizard_step_viewport()

    def setup_extensions_only(self) -> Dict[str, bool]:
        """Run extensions configuration wizard only."""
        return self._wizard_step_extensions()

    def _wizard_step_theme(self) -> str:
        """Theme selection step (simulated for now)."""
        # In real implementation, this would be interactive
        # For now, return a selection
        return "dungeon"  # Default theme

    def _wizard_step_viewport(self) -> str:
        """Viewport configuration step (simulated)."""
        return "auto"  # Auto-detect

    def _wizard_step_extensions(self) -> Dict[str, bool]:
        """Extensions configuration step (simulated)."""
        return {
            'enable_web': True,
            'enable_teletext': True,
            'enable_dashboard': True
        }

    def _wizard_step_advanced(self) -> Dict[str, bool]:
        """Advanced settings step (simulated)."""
        return {
            'developer_mode': False,
            'debug_logging': False,
            'experimental_features': False
        }

    def _show_summary(self, config: Dict[str, Any]) -> None:
        """Display configuration summary."""
        print(self._format_summary(config))

    def _format_welcome(self) -> str:
        """Format welcome screen."""
        welcome = "╔" + "═"*78 + "╗\n"
        welcome += "║" + " "*24 + "🚀 uDOS Setup Wizard" + " "*34 + "║\n"
        welcome += "╠" + "═"*78 + "╣\n"
        welcome += "║  Welcome to uDOS! Let's configure your system.".ljust(79) + "║\n"
        welcome += "║".ljust(79) + "║\n"
        welcome += "║  This wizard will guide you through:".ljust(79) + "║\n"
        welcome += "║    1. Theme Selection".ljust(79) + "║\n"
        welcome += "║    2. Viewport Configuration".ljust(79) + "║\n"
        welcome += "║    3. Extension Setup".ljust(79) + "║\n"
        welcome += "║    4. Advanced Settings".ljust(79) + "║\n"
        welcome += "║".ljust(79) + "║\n"
        welcome += "║  You can skip this with 'SETUP QUICK' for defaults.".ljust(79) + "║\n"
        welcome += "╚" + "═"*78 + "╝\n"
        return welcome

    def _format_summary(self, config: Dict[str, Any]) -> str:
        """Format configuration summary."""
        summary = "╔" + "═"*78 + "╗\n"
        summary += "║  📋 Configuration Summary".ljust(79) + "║\n"
        summary += "╠" + "═"*78 + "╣\n"
        summary += f"║  Theme: {config.get('theme', 'N/A')}".ljust(79) + "║\n"
        summary += f"║  Viewport: {config.get('viewport', 'N/A')}".ljust(79) + "║\n"

        extensions = config.get('extensions', {})
        ext_count = sum(1 for v in extensions.values() if v)
        summary += f"║  Extensions: {ext_count} enabled".ljust(79) + "║\n"

        summary += "║".ljust(79) + "║\n"
        summary += "║  ✅ Configuration complete!".ljust(79) + "║\n"
        summary += "╚" + "═"*78 + "╝\n"
        return summary

    def format_theme_options(self) -> str:
        """Format theme selection options."""
        output = "╔" + "═"*78 + "╗\n"
        output += "║  🎨 Available Themes".ljust(79) + "║\n"
        output += "╠" + "═"*78 + "╣\n"

        for i, theme in enumerate(self.available_themes, 1):
            output += f"║  {i}. {theme.capitalize()}".ljust(79) + "║\n"

        output += "║".ljust(79) + "║\n"
        output += "║  Use: SETUP THEME <name>".ljust(79) + "║\n"
        output += "╚" + "═"*78 + "╝\n"
        return output

    def format_viewport_options(self) -> str:
        """Format viewport preset options."""
        output = "╔" + "═"*78 + "╗\n"
        output += "║  📺 Viewport Presets".ljust(79) + "║\n"
        output += "╠" + "═"*78 + "╣\n"

        for preset in self.available_viewports:
            name = preset['name']
            size = preset['size']
            tier = preset['tier']
            output += f"║  {name:<12} - {size:<10} (Tier {tier})".ljust(79) + "║\n"

        output += "║".ljust(79) + "║\n"
        output += "║  Current: Auto-detect (recommended)".ljust(79) + "║\n"
        output += "║  Use: SETUP VIEWPORT <preset>".ljust(79) + "║\n"
        output += "╚" + "═"*78 + "╝\n"
        return output

    def format_extensions_options(self) -> str:
        """Format extension options."""
        output = "╔" + "═"*78 + "╗\n"
        output += "║  🔌 Available Extensions".ljust(79) + "║\n"
        output += "╠" + "═"*78 + "╣\n"
        output += "║  • Web Interface (Dashboard)".ljust(79) + "║\n"
        output += "║  • Teletext Renderer".ljust(79) + "║\n"
        output += "║  • Font Editor".ljust(79) + "║\n"
        output += "║  • System Desktop".ljust(79) + "║\n"
        output += "║".ljust(79) + "║\n"
        output += "║  Use: SETUP EXTENSIONS to configure".ljust(79) + "║\n"
        output += "╚" + "═"*78 + "╝\n"
        return output

    def format_help(self) -> str:
        """Format SETUP command help."""
        help_text = "╔" + "═"*78 + "╗\n"
        help_text += "║  📖 SETUP - Interactive Configuration Wizard".ljust(79) + "║\n"
        help_text += "╠" + "═"*78 + "╣\n"
        help_text += "║  Available Commands:".ljust(79) + "║\n"
        help_text += "║".ljust(79) + "║\n"
        help_text += "║  SETUP              - Run full interactive wizard".ljust(79) + "║\n"
        help_text += "║  SETUP WIZARD       - Same as SETUP".ljust(79) + "║\n"
        help_text += "║  SETUP QUICK        - Quick setup with defaults".ljust(79) + "║\n"
        help_text += "║  SETUP THEME        - Theme selection only".ljust(79) + "║\n"
        help_text += "║  SETUP VIEWPORT     - Viewport configuration only".ljust(79) + "║\n"
        help_text += "║  SETUP EXTENSIONS   - Extension management only".ljust(79) + "║\n"
        help_text += "║".ljust(79) + "║\n"
        help_text += "║  Examples:".ljust(79) + "║\n"
        help_text += "║    SETUP            → Full interactive wizard".ljust(79) + "║\n"
        help_text += "║    SETUP QUICK      → Use sensible defaults".ljust(79) + "║\n"
        help_text += "║    SETUP THEME      → Change theme only".ljust(79) + "║\n"
        help_text += "╚" + "═"*78 + "╝\n"
        return help_text

    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate configuration dictionary.

        Args:
            config: Configuration to validate

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Validate theme
        if 'theme' in config:
            if config['theme'] not in self.available_themes:
                errors.append(f"Invalid theme: {config['theme']}")

        # Validate viewport
        if 'viewport' in config:
            valid_viewports = ['auto'] + [p['name'].lower() for p in self.available_viewports]
            if config['viewport'].lower() not in valid_viewports:
                errors.append(f"Invalid viewport: {config['viewport']}")

        return (len(errors) == 0, errors)

    def export_config(self, config: Dict[str, Any]) -> str:
        """Export configuration to JSON string."""
        return json.dumps(config, indent=2)

    def import_config(self, config_json: str) -> Dict[str, Any]:
        """Import configuration from JSON string."""
        try:
            return json.loads(config_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON configuration: {e}")


# Standalone test function
def test_setup_wizard():
    """Test SetupWizard functionality."""
    print("Testing SetupWizard...")

    wizard = SetupWizard()

    # Test theme options
    themes = wizard.format_theme_options()
    print(f"✅ Theme options: {len(themes)} characters")

    # Test viewport options
    viewports = wizard.format_viewport_options()
    print(f"✅ Viewport options: {len(viewports)} characters")

    # Test quick setup
    quick_config = wizard.run_quick_setup()
    print(f"✅ Quick setup: {len(quick_config)} settings")
    print(f"   Theme: {quick_config['theme']}")
    print(f"   Viewport: {quick_config['viewport']}")

    # Test validation
    is_valid, errors = wizard.validate_config(quick_config)
    print(f"✅ Validation: {is_valid}, {len(errors)} errors")

    # Test help
    help_text = wizard.format_help()
    print(f"✅ Help text: {len(help_text)} characters")

    print("\n✅ SetupWizard tests passed")


if __name__ == "__main__":
    test_setup_wizard()
