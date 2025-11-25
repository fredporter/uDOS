"""
Design Assets Manager
Centralized asset management for ASCII, Teletext, and SVG formats
"""

from pathlib import Path
from typing import Dict, Optional, Literal


class DesignAssets:
    """
    Centralized asset management for OK Assist unified design system

    Maps visual elements across ASCII, Teletext, and SVG formats with
    C64 PetMe as the reference character set.
    """

    ASSETS_ROOT = Path(__file__).parent.parent.parent / "assets"

    # Font mappings
    FONTS = {
        "ascii": {
            "regular": "petme/PetMe64.ttf",
            "double_width": "petme/PetMe2X.ttf",
            "double_height": "petme/PetMe2Y.ttf",
        },
        "teletext": {
            "regular": "petme/PetMe64.ttf",  # Fallback
            "double_height": "petme/PetMe2Y.ttf",
        },
        "svg_technical": {
            "title": "ChiKareGo2.woff2",  # Chicago 12pt
            "body": "FindersKeepers.woff2",  # Geneva 9pt
            "mono": "monaco.woff2",
        },
        "svg_organic": {
            "title": "FindersKeepers.woff2",  # Geneva 14pt italic
            "body": "FindersKeepers.woff2",  # Geneva 10pt
            "caption": "FindersKeepers.woff2",  # Geneva 8pt italic
        }
    }

    # Icon mappings across formats
    ICONS = {
        "tool": {
            "ascii": "⚒",
            "teletext": "&#xE23F;",
            "svg": "cil-wrench"
        },
        "check": {
            "ascii": "✓",
            "teletext": "☑",
            "svg": "cil-check-circle"
        },
        "warning": {
            "ascii": "⚠",
            "teletext": "⚠",
            "svg": "cil-warning"
        },
        "arrow_right": {
            "ascii": "→",
            "teletext": "►",
            "svg": "cil-arrow-right"
        },
        "arrow_left": {
            "ascii": "←",
            "teletext": "◄",
            "svg": "cil-arrow-left"
        },
        "arrow_up": {
            "ascii": "↑",
            "teletext": "▲",
            "svg": "cil-arrow-top"
        },
        "arrow_down": {
            "ascii": "↓",
            "teletext": "▼",
            "svg": "cil-arrow-bottom"
        },
        "heart": {
            "ascii": "♥",
            "teletext": "♥",
            "svg": "cil-heart"
        },
        "tree": {
            "ascii": "🌲",
            "teletext": "▲",
            "svg": "custom-tree"
        },
        "water": {
            "ascii": "≈",
            "teletext": "~",
            "svg": "cil-drop"
        },
        "fire": {
            "ascii": "🔥",
            "teletext": "▲",
            "svg": "cil-fire"
        },
        "star": {
            "ascii": "★",
            "teletext": "*",
            "svg": "cil-star"
        }
    }

    # Pattern/texture mappings
    PATTERNS = {
        "solid": {
            "ascii": "████",
            "teletext": "&#xE23F;",  # Full block
            "svg_tech": "gray-87",
            "svg_organic": "solid-fill"
        },
        "metal": {
            "ascii": "▓▓▓▓",
            "teletext": "&#xE240;",  # Separated mosaic
            "svg_tech": "crosshatch",
            "svg_organic": "parallel-lines"
        },
        "wood": {
            "ascii": "≡≡≡≡",
            "teletext": "─",
            "svg_tech": "diagonal",
            "svg_organic": "woodgrain"
        },
        "water": {
            "ascii": "≈≈≈≈",
            "teletext": "~",
            "svg_tech": "horizontal",
            "svg_organic": "ripples"
        },
        "grass": {
            "ascii": "∴∴∴∴",
            "teletext": ".",
            "svg_tech": "dots",
            "svg_organic": "wavy-parallel"
        },
        "stone": {
            "ascii": "▒▒▒▒",
            "teletext": "&#xE233;",  # Checkerboard
            "svg_tech": "gray-50",
            "svg_organic": "crack-lines"
        },
        "light": {
            "ascii": "░░░░",
            "teletext": "&#xE215;",  # Left half
            "svg_tech": "gray-12",
            "svg_organic": "light-stipple"
        },
        "medium": {
            "ascii": "▒▒▒▒",
            "teletext": "&#xE233;",
            "svg_tech": "gray-50",
            "svg_organic": "medium-hatch"
        },
        "dark": {
            "ascii": "▓▓▓▓",
            "teletext": "&#xE22A;",  # Right half
            "svg_tech": "gray-75",
            "svg_organic": "dense-stipple"
        }
    }

    # Teletext mosaic mappings
    TELETEXT_MOSAICS = {
        "empty": "&#xE200;",      # 000000
        "full": "&#xE23F;",       # 111111
        "left_half": "&#xE215;",  # 101010
        "right_half": "&#xE22A;", # 010101
        "top_half": "&#xE203;",   # 110000
        "bottom_half": "&#xE230;",# 001100
        "corners": "&#xE233;",    # 110011
        "sides": "&#xE20C;",      # 001100
        "tl_quad": "&#xE221;",    # Top-left quarter
        "tr_quad": "&#xE222;",    # Top-right quarter
        "bl_quad": "&#xE224;",    # Bottom-left quarter
        "br_quad": "&#xE228;",    # Bottom-right quarter
    }

    # ASCII to Teletext mosaic mapping
    ASCII_TO_TELETEXT = {
        ' ': '&#xE200;',  # Empty
        '█': '&#xE23F;',  # Full
        '▌': '&#xE215;',  # Left half
        '▐': '&#xE22A;',  # Right half
        '▀': '&#xE203;',  # Top half
        '▄': '&#xE230;',  # Bottom half
        '▘': '&#xE221;',  # Top-left quarter
        '▝': '&#xE222;',  # Top-right quarter
        '▖': '&#xE224;',  # Bottom-left quarter
        '▗': '&#xE228;',  # Bottom-right quarter
        '░': '&#xE215;',  # Light shade → left half
        '▒': '&#xE233;',  # Medium shade → corners
        '▓': '&#xE22A;',  # Dark shade → right half
    }

    # WST color palette
    WST_COLORS = {
        "BLACK": "#000000",
        "RED": "#FF0000",
        "GREEN": "#00FF00",
        "YELLOW": "#FFFF00",
        "BLUE": "#0000FF",
        "MAGENTA": "#FF00FF",
        "CYAN": "#00FFFF",
        "WHITE": "#FFFFFF"
    }

    # Color to greyscale mapping
    COLOR_TO_GREY = {
        "BLACK": "#000000",    # 0%
        "BLUE": "#333333",     # 20%
        "RED": "#555555",      # 33%
        "MAGENTA": "#666666",  # 40%
        "GREEN": "#888888",    # 53%
        "CYAN": "#AAAAAA",     # 67%
        "YELLOW": "#CCCCCC",   # 80%
        "WHITE": "#FFFFFF",    # 100%
    }

    @classmethod
    def get_font_path(cls, format: str, variant: str = "regular") -> Path:
        """Get font file path for format"""
        font_map = cls.FONTS.get(format, {})
        font_file = font_map.get(variant)
        if not font_file:
            raise ValueError(f"Unknown font variant '{variant}' for format '{format}'")
        return cls.ASSETS_ROOT / "fonts" / font_file

    @classmethod
    def get_icon(cls, concept: str, format: str) -> str:
        """Get icon representation for concept in format"""
        icon_map = cls.ICONS.get(concept, {})
        icon = icon_map.get(format)
        if not icon:
            return ""  # Return empty if not mapped
        return icon

    @classmethod
    def get_pattern(cls, texture: str, format: str) -> str:
        """Get pattern/texture definition for format"""
        pattern_map = cls.PATTERNS.get(texture, {})
        pattern = pattern_map.get(format)
        if not pattern:
            return ""
        return pattern

    @classmethod
    def ascii_to_teletext(cls, ascii_char: str) -> str:
        """Convert ASCII block character to Teletext mosaic entity"""
        return cls.ASCII_TO_TELETEXT.get(ascii_char, ascii_char)

    @classmethod
    def teletext_to_ascii(cls, teletext_entity: str) -> str:
        """Convert Teletext mosaic entity to ASCII block character"""
        # Reverse lookup
        for ascii_char, entity in cls.ASCII_TO_TELETEXT.items():
            if entity == teletext_entity:
                return ascii_char
        return ' '  # Default to space

    @classmethod
    def color_to_greyscale(cls, color: str) -> str:
        """Convert WST color name to greyscale hex"""
        return cls.COLOR_TO_GREY.get(color.upper(), "#808080")

    @classmethod
    def get_wst_color(cls, color: str) -> str:
        """Get WST color hex value"""
        return cls.WST_COLORS.get(color.upper(), "#FFFFFF")


# Convenience functions
def get_icon_for_format(concept: str, format: Literal["ascii", "teletext", "svg"]) -> str:
    """Quick icon lookup"""
    return DesignAssets.get_icon(concept, format)


def map_ascii_to_teletext(ascii_art: str) -> str:
    """Convert ASCII art string to Teletext entities"""
    result = []
    for char in ascii_art:
        result.append(DesignAssets.ascii_to_teletext(char))
    return ''.join(result)


def get_pattern_for_format(texture: str, format: Literal["ascii", "teletext", "svg_tech", "svg_organic"]) -> str:
    """Quick pattern lookup"""
    return DesignAssets.get_pattern(texture, format)


# Example usage
if __name__ == "__main__":
    print("Design Assets Manager - OK Assist Unified System\n")

    # Font paths
    print("Font Paths:")
    print(f"  ASCII Regular: {DesignAssets.get_font_path('ascii', 'regular')}")
    print(f"  SVG Technical: {DesignAssets.get_font_path('svg_technical', 'title')}")
    print(f"  SVG Organic:   {DesignAssets.get_font_path('svg_organic', 'title')}")

    # Icons
    print("\nIcon Mappings:")
    for concept in ["tool", "check", "warning", "arrow_right"]:
        print(f"  {concept:12} → ASCII: {DesignAssets.get_icon(concept, 'ascii'):5} "
              f"Teletext: {DesignAssets.get_icon(concept, 'teletext'):12} "
              f"SVG: {DesignAssets.get_icon(concept, 'svg')}")

    # Patterns
    print("\nPattern Mappings:")
    for texture in ["solid", "metal", "wood", "water"]:
        print(f"  {texture:8} → ASCII: {DesignAssets.get_pattern(texture, 'ascii'):6} "
              f"SVG Tech: {DesignAssets.get_pattern(texture, 'svg_tech'):12} "
              f"SVG Organic: {DesignAssets.get_pattern(texture, 'svg_organic')}")

    # Conversions
    print("\nASCII → Teletext Conversions:")
    ascii_blocks = "█▌▐▀▄░▒▓"
    for char in ascii_blocks:
        teletext = DesignAssets.ascii_to_teletext(char)
        print(f"  {char} → {teletext}")

    # Colors
    print("\nWST Color → Greyscale:")
    for color in ["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE"]:
        wst = DesignAssets.get_wst_color(color)
        grey = DesignAssets.color_to_greyscale(color)
        print(f"  {color:8} {wst} → {grey}")
