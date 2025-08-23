#!/usr/bin/env python3
"""
uMEMORY System Configuration Loader
Part of the uDOS System Architecture

This module loads and manages system configurations from the centralized
uMEMORY/system directory including fonts, colors, and system settings.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

class uMemoryConfigLoader:
    """Centralized configuration loader for uDOS system"""
    
    def __init__(self, udos_root: Optional[str] = None):
        """Initialize the configuration loader"""
        self.udos_root = Path(udos_root) if udos_root else self._find_udos_root()
        self.umemory_path = self.udos_root / "uMEMORY"
        self.system_path = self.umemory_path / "system"
        
        # Configuration paths
        self.fonts_path = self.system_path / "fonts"
        self.colors_path = self.system_path / "colors"
        self.config_path = self.system_path / "config"
        
        # Loaded configurations cache
        self._font_registry = None
        self._color_palettes = None
        self._system_config = None
        
    def _find_udos_root(self) -> Path:
        """Find the uDOS root directory"""
        current = Path.cwd()
        
        # Look for uDOS markers
        while current != current.parent:
            if (current / "uMEMORY").exists() and (current / "uCORE").exists():
                return current
            current = current.parent
            
        # Default to current directory
        return Path.cwd()
    
    def load_font_registry(self) -> Dict[str, Any]:
        """Load the font registry from uMEMORY/system/fonts"""
        if self._font_registry is not None:
            return self._font_registry
            
        registry_file = self.fonts_path / "font-registry.json"
        if not registry_file.exists():
            print(f"Warning: Font registry not found at {registry_file}")
            return {}
            
        try:
            with open(registry_file, 'r') as f:
                self._font_registry = json.load(f)
            return self._font_registry
        except Exception as e:
            print(f"Error loading font registry: {e}")
            return {}
    
    def load_color_palettes(self) -> Dict[str, Any]:
        """Load color palettes from uMEMORY/system/colors"""
        if self._color_palettes is not None:
            return self._color_palettes
            
        palettes_file = self.colors_path / "color-palettes.json"
        if not palettes_file.exists():
            print(f"Warning: Color palettes not found at {palettes_file}")
            return {}
            
        try:
            with open(palettes_file, 'r') as f:
                self._color_palettes = json.load(f)
            return self._color_palettes
        except Exception as e:
            print(f"Error loading color palettes: {e}")
            return {}
    
    def load_system_config(self) -> Dict[str, Any]:
        """Load system configuration from uMEMORY/system/config"""
        if self._system_config is not None:
            return self._system_config
            
        config_file = self.config_path / "system-config.json"
        if not config_file.exists():
            print(f"Warning: System config not found at {config_file}")
            return {}
            
        try:
            with open(config_file, 'r') as f:
                self._system_config = json.load(f)
            return self._system_config
        except Exception as e:
            print(f"Error loading system config: {e}")
            return {}
    
    def get_font_info(self, font_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific font"""
        registry = self.load_font_registry()
        
        # Check direct fonts structure first
        fonts = registry.get("fonts", {})
        if font_name in fonts:
            return fonts[font_name]
            
        # Check nested structure
        font_registry = registry.get("font_registry", {})
        bbc_fonts = font_registry.get("bbc_mode7_fonts", {})
        retro_fonts = font_registry.get("retro_fonts", {})
        
        if font_name in bbc_fonts:
            return bbc_fonts[font_name]
        elif font_name in retro_fonts:
            return retro_fonts[font_name]
            
        return None
    
    def get_available_fonts(self) -> List[str]:
        """Get list of available font names"""
        registry = self.load_font_registry()
        fonts = []
        
        # Check both possible structures
        font_data = registry.get("fonts", {})
        if not font_data:
            # Try nested structure
            font_registry = registry.get("font_registry", {})
            bbc_fonts = font_registry.get("bbc_mode7_fonts", {})
            retro_fonts = font_registry.get("retro_fonts", {})
            fonts.extend(list(bbc_fonts.keys()))
            fonts.extend(list(retro_fonts.keys()))
        else:
            fonts = list(font_data.keys())
            
        return fonts
    
    def get_font_path(self, font_name: str) -> Optional[Path]:
        """Get the file path for a specific font"""
        font_info = self.get_font_info(font_name)
        if not font_info:
            return None
            
        # Try different filename keys
        filename = font_info.get("filename") or font_info.get("file")
        if not filename:
            return None
            
        return self.fonts_path / filename
    
    def get_color_palette(self, palette_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific color palette"""
        palettes = self.load_color_palettes()
        
        # Handle color_palettes structure
        color_palettes = palettes.get("color_palettes", {})
        return color_palettes.get(palette_name)
    
    def get_available_palettes(self) -> List[str]:
        """Get list of available color palette names"""
        palettes = self.load_color_palettes()
        
        # Handle color_palettes structure
        color_palettes = palettes.get("color_palettes", {})
        
        # Get all keys except metadata
        palette_names = []
        for key, value in color_palettes.items():
            if key != "metadata" and isinstance(value, dict) and "colors" in value:
                palette_names.append(key)
        
        return palette_names
    
    def get_css_colors(self, palette_name: str) -> Dict[str, str]:
        """Get CSS color variables for a palette"""
        palettes = self.load_color_palettes()
        css_vars = palettes.get("css_variables", {})
        return css_vars.get(palette_name, {})
    
    def get_display_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific display configuration"""
        config = self.load_system_config()
        displays = config.get("system_config", {}).get("display_configurations", {})
        return displays.get(config_name)
    
    def get_default_display_config(self) -> Dict[str, Any]:
        """Get the default display configuration"""
        config = self.load_system_config()
        
        # Find the recommended display config
        displays = config.get("system_config", {}).get("display_configurations", {})
        for name, display_config in displays.items():
            if display_config.get("recommended", False):
                return {"name": name, **display_config}
        
        # Fall back to first available or udos_optimized
        if "udos_optimized" in displays:
            return {"name": "udos_optimized", **displays["udos_optimized"]}
        
        if displays:
            first_name = list(displays.keys())[0]
            return {"name": first_name, **displays[first_name]}
        
        # Ultimate fallback
        return {
            "name": "fallback",
            "width": 800,
            "height": 615,
            "font": "MODE7GX3",
            "theme": "udos_vibrant_dark"
        }
    
    def get_interface_mode(self, mode_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific interface mode configuration"""
        config = self.load_system_config()
        modes = config.get("system_config", {}).get("interface_modes", {})
        return modes.get(mode_name)
    
    def get_system_paths(self) -> Dict[str, str]:
        """Get system path configurations"""
        config = self.load_system_config()
        paths = config.get("system_config", {}).get("system_defaults", {}).get("paths", {})
        
        # Convert relative paths to absolute
        absolute_paths = {}
        for key, path in paths.items():
            if path.startswith("/"):
                # Already absolute, but make it relative to uDOS root
                absolute_paths[key] = str(self.udos_root / path.lstrip("/"))
            else:
                absolute_paths[key] = str(self.udos_root / path)
                
        return absolute_paths
    
    def validate_configuration(self) -> Dict[str, bool]:
        """Validate that all configuration files and directories exist"""
        validation = {
            "umemory_exists": self.umemory_path.exists(),
            "system_exists": self.system_path.exists(),
            "fonts_dir_exists": self.fonts_path.exists(),
            "colors_dir_exists": self.colors_path.exists(),
            "config_dir_exists": self.config_path.exists(),
            "font_registry_exists": (self.fonts_path / "font-registry.json").exists(),
            "color_palettes_exists": (self.colors_path / "color-palettes.json").exists(),
            "system_config_exists": (self.config_path / "system-config.json").exists(),
        }
        
        # Check if font files exist
        font_registry = self.load_font_registry()
        validation["font_files_exist"] = True
        for font_name, font_info in font_registry.get("fonts", {}).items():
            filename = font_info.get("filename")
            if filename and not (self.fonts_path / filename).exists():
                validation["font_files_exist"] = False
                break
        
        return validation
    
    def generate_css_variables(self, palette_name: str = "udos_vibrant") -> str:
        """Generate CSS variable declarations for a color palette"""
        colors = self.get_css_colors(palette_name)
        if not colors:
            return "/* No CSS variables found for palette: {} */".format(palette_name)
        
        css_lines = [f"/* CSS Variables for {palette_name} palette */", ":root {"]
        for var_name, color_value in colors.items():
            css_lines.append(f"    --{var_name}: {color_value};")
        css_lines.append("}")
        
        return "\n".join(css_lines)
    
    def get_startup_config(self) -> Dict[str, Any]:
        """Get startup configuration"""
        config = self.load_system_config()
        return config.get("system_config", {}).get("system_defaults", {}).get("startup", {})


def main():
    """CLI interface for testing the configuration loader"""
    import argparse
    
    parser = argparse.ArgumentParser(description="uMEMORY Configuration Loader")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    parser.add_argument("--list-fonts", action="store_true", help="List available fonts")
    parser.add_argument("--list-palettes", action="store_true", help="List available color palettes")
    parser.add_argument("--font-info", type=str, help="Get info about a specific font")
    parser.add_argument("--palette-info", type=str, help="Get info about a specific palette")
    parser.add_argument("--css-vars", type=str, help="Generate CSS variables for palette")
    parser.add_argument("--default-display", action="store_true", help="Show default display config")
    
    args = parser.parse_args()
    
    # Initialize loader
    loader = uMemoryConfigLoader()
    
    if args.validate:
        print("Validating uMEMORY configuration...")
        validation = loader.validate_configuration()
        for check, result in validation.items():
            status = "✓" if result else "✗"
            print(f"{status} {check}: {result}")
        return
    
    if args.list_fonts:
        fonts = loader.get_available_fonts()
        print(f"Available fonts ({len(fonts)}):")
        for font in fonts:
            print(f"  - {font}")
        return
    
    if args.list_palettes:
        palettes = loader.get_available_palettes()
        print(f"Available color palettes ({len(palettes)}):")
        for palette in palettes:
            print(f"  - {palette}")
        return
    
    if args.font_info:
        info = loader.get_font_info(args.font_info)
        if info:
            print(f"Font info for '{args.font_info}':")
            for key, value in info.items():
                print(f"  {key}: {value}")
        else:
            print(f"Font '{args.font_info}' not found")
        return
    
    if args.palette_info:
        info = loader.get_color_palette(args.palette_info)
        if info:
            print(f"Palette info for '{args.palette_info}':")
            for key, value in info.items():
                print(f"  {key}: {value}")
        else:
            print(f"Palette '{args.palette_info}' not found")
        return
    
    if args.css_vars:
        css = loader.generate_css_variables(args.css_vars)
        print(css)
        return
    
    if args.default_display:
        config = loader.get_default_display_config()
        print("Default display configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        return
    
    # Default: show summary
    print("uMEMORY Configuration Loader")
    print(f"uDOS Root: {loader.udos_root}")
    print(f"uMEMORY Path: {loader.umemory_path}")
    
    validation = loader.validate_configuration()
    if all(validation.values()):
        print("✓ Configuration is valid")
    else:
        print("✗ Configuration has issues")
        for check, result in validation.items():
            if not result:
                print(f"  ✗ {check}")


if __name__ == "__main__":
    main()
