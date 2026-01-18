"""
Emoji Mapping Service for Wizard Server
=======================================

Provides shortcode → emoji rendering with mono/color variants.

Examples:
  :padlock: → 🔐 (color) or use mono variant
  :gear: → ⚙️
  :checkmark: → ✓

Usage:
  from wizard.services.emoji_map import emoji_shortcode, EmojiStyle

  # Render with mono emoji (default for HTTP UI)
  html = emoji_shortcode(":padlock: Encryption enabled", style=EmojiStyle.MONO)

  # Render with color emoji (for TUI only)
  text = emoji_shortcode(":gear: Setup", style=EmojiStyle.COLOR)
"""

from enum import Enum
from typing import Dict, Optional

class EmojiStyle(str, Enum):
    """Emoji rendering style."""
    MONO = "mono"      # NotoEmoji-Regular (monochrome)
    COLOR = "color"    # NotoColorEmoji (colorful)


# Core emoji shortcode mapping
EMOJI_MAP: Dict[str, str] = {
    # Security
    "padlock": "🔐",
    "lock": "🔒",
    "unlock": "🔓",
    "key": "🔑",
    "shield": "🛡️",

    # Status
    "checkmark": "✓",
    "check": "✓",
    "cross": "✗",
    "x": "✗",
    "warning": "⚠️",
    "error": "❌",
    "success": "✅",
    "info": "ℹ️",

    # System
    "gear": "⚙️",
    "wrench": "🔧",
    "hammer": "🔨",
    "cog": "⚙️",
    "settings": "⚙️",

    # Navigation
    "right": "→",
    "left": "←",
    "up": "↑",
    "down": "↓",
    "arrow-right": "→",
    "arrow-left": "←",
    "arrow-up": "↑",
    "arrow-down": "↓",

    # Status indicators
    "dot": "●",
    "circle": "○",
    "square": "□",
    "triangle": "△",

    # Common UI
    "plus": "➕",
    "minus": "➖",
    "multiply": "✖️",
    "divide": "➗",
    "equals": "＝",
    "dash": "–",

    # Database
    "database": "🗄️",
    "table": "📋",
    "file": "📄",
    "folder": "📁",

    # Notifications
    "bell": "🔔",
    "clock": "🕐",
    "calendar": "📅",

    # Development
    "code": "💻",
    "terminal": "💻",
    "bug": "🐛",
    "debug": "🐛",
    "rocket": "🚀",
    "fire": "🔥",

    # General
    "star": "⭐",
    "heart": "❤️",
    "thumbs-up": "👍",
    "thumbs-down": "👎",
}


def emoji_shortcode(
    text: str,
    style: EmojiStyle = EmojiStyle.MONO
) -> str:
    """
    Convert emoji shortcodes in text to actual emoji characters.

    Args:
        text: Text containing :shortcode: patterns
        style: EmojiStyle.MONO or EmojiStyle.COLOR

    Returns:
        Text with emoji rendered and styled appropriately

    Example:
        emoji_shortcode(":checkmark: Success!", style=EmojiStyle.MONO)
        # Returns: "✓ Success!" with mono font styling
    """
    import re

    def replace_shortcode(match):
        shortcode = match.group(1).lower()
        emoji = EMOJI_MAP.get(shortcode, match.group(0))

        # Wrap with appropriate CSS class
        if style == EmojiStyle.MONO:
            return f'<span class="emoji-mono">{emoji}</span>'
        else:
            return f'<span class="emoji-color">{emoji}</span>'

    # Pattern: :word: or :multi-word: or :multi_word:
    pattern = r':([a-z0-9\-_]+):'
    return re.sub(pattern, replace_shortcode, text, flags=re.IGNORECASE)


def emoji_to_html(
    text: str,
    style: EmojiStyle = EmojiStyle.MONO,
    css_class: Optional[str] = None
) -> str:
    """
    Convert shortcodes and wrap output in HTML with proper font selection.

    Args:
        text: Text with shortcodes
        style: Mono or color emoji
        css_class: Additional CSS classes to apply

    Returns:
        HTML string with styled emoji

    Example:
        html = emoji_to_html(":gear: Settings", style=EmojiStyle.MONO, css_class="text-lg")
    """
    classes = []
    if style == EmojiStyle.MONO:
        classes.append("emoji-mono")
    else:
        classes.append("emoji-color")

    if css_class:
        classes.append(css_class)

    class_str = " ".join(classes)
    content = emoji_shortcode(text, style)

    return f'<div class="{class_str}">{content}</div>'


def get_emoji(shortcode: str, style: EmojiStyle = EmojiStyle.MONO) -> str:
    """
    Get single emoji character by shortcode.

    Args:
        shortcode: Emoji name without colons (e.g., "padlock")
        style: Mono or color

    Returns:
        Emoji character or original shortcode if not found

    Example:
        emoji = get_emoji("checkmark")  # Returns "✓"
    """
    emoji = EMOJI_MAP.get(shortcode.lower())
    if not emoji:
        return f":{shortcode}:"

    if style == EmojiStyle.MONO:
        return f'<span class="emoji-mono">{emoji}</span>'
    else:
        return f'<span class="emoji-color">{emoji}</span>'


def emoji_exists(shortcode: str) -> bool:
    """Check if emoji shortcode is defined."""
    return shortcode.lower() in EMOJI_MAP


def list_emoji() -> Dict[str, str]:
    """Get all available emoji mappings."""
    return EMOJI_MAP.copy()


def get_emoji_categories() -> Dict[str, list]:
    """Get emoji organized by category."""
    return {
        "security": ["padlock", "lock", "unlock", "key", "shield"],
        "status": ["checkmark", "check", "cross", "x", "warning", "error", "success", "info"],
        "system": ["gear", "wrench", "hammer", "cog", "settings"],
        "navigation": ["right", "left", "up", "down", "arrow-right", "arrow-left", "arrow-up", "arrow-down"],
        "indicators": ["dot", "circle", "square", "triangle"],
        "ui": ["plus", "minus", "multiply", "divide", "equals", "dash"],
        "database": ["database", "table", "file", "folder"],
        "notifications": ["bell", "clock", "calendar"],
        "development": ["code", "terminal", "bug", "debug", "rocket", "fire"],
        "general": ["star", "heart", "thumbs-up", "thumbs-down"],
    }


# HTML templates for common patterns

def icon_label(icon: str, label: str, style: EmojiStyle = EmojiStyle.MONO) -> str:
    """
    Create an icon + label pattern.

    Args:
        icon: Shortcode or emoji character
        label: Label text
        style: Emoji style

    Returns:
        HTML: <span class="icon-label"><emoji> Label</span>

    Example:
        html = icon_label("checkmark", "Validated", EmojiStyle.MONO)
    """
    emoji = get_emoji(icon, style) if icon.startswith(":") or icon in EMOJI_MAP else icon
    return f'<span class="icon-label">{emoji} {label}</span>'


def status_badge(status: str, label: str, style: EmojiStyle = EmojiStyle.MONO) -> str:
    """
    Create a status badge with emoji and label.

    Args:
        status: "success", "warning", "error", "info"
        label: Badge label text
        style: Emoji style

    Returns:
        HTML: <span class="badge badge-{status}"><emoji> Label</span>

    Example:
        html = status_badge("success", "Configuration Valid", EmojiStyle.MONO)
    """
    icon_map = {
        "success": "checkmark",
        "warning": "warning",
        "error": "error",
        "info": "info",
    }
    icon = icon_map.get(status, "info")
    emoji = get_emoji(icon, style)
    return f'<span class="badge badge-{status}">{emoji} {label}</span>'


if __name__ == "__main__":
    # Test the emoji mapper
    print("Testing Emoji Mapper")
    print("=" * 50)

    # Test shortcode conversion
    text = ":padlock: Encryption :checkmark: Status: :gear: Settings"
    print(f"Input:  {text}")
    print(f"Mono:   {emoji_shortcode(text, EmojiStyle.MONO)}")
    print(f"Color:  {emoji_shortcode(text, EmojiStyle.COLOR)}")
    print()

    # Test single emoji
    print(f"Single emoji: {get_emoji('checkmark', EmojiStyle.MONO)}")
    print()

    # Test status badge
    print(f"Badge: {status_badge('success', 'All systems operational', EmojiStyle.MONO)}")
    print()

    # List available emoji
    print("Available emoji shortcodes:")
    for shortcode in sorted(EMOJI_MAP.keys()):
        print(f"  :{shortcode}: → {EMOJI_MAP[shortcode]}")
