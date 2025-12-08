"""
uDOS v1.0.21 - PANEL Command Handler

Control teletext-style display panels with definable boundaries.
Panels can be:
- Displayed in teletext mode (C64-style with border)
- Embedded in markdown files
- Used for uSCRIPT output display
- POKE'd with character data
"""

from .base_handler import BaseCommandHandler
import os
from pathlib import Path


class PanelCommandHandler(BaseCommandHandler):
    """Handles PANEL command for teletext-style displays."""

    # Screen tiers with character dimensions
    SCREEN_TIERS = {
        0: {"name": "Watch", "chars": (20, 10)},
        1: {"name": "Watch Large", "chars": (24, 12)},
        2: {"name": "Phone Portrait", "chars": (30, 40)},
        3: {"name": "Phone Landscape", "chars": (40, 24)},
        4: {"name": "Tablet Portrait", "chars": (40, 60)},
        5: {"name": "Tablet Landscape", "chars": (60, 40)},
        6: {"name": "Laptop", "chars": (80, 24)},
        7: {"name": "Desktop", "chars": (80, 40)},
        8: {"name": "Desktop Large", "chars": (100, 40)},
        9: {"name": "4K", "chars": (120, 60)},
        10: {"name": "4K Large", "chars": (160, 80)},
        11: {"name": "5K", "chars": (180, 90)},
        12: {"name": "6K", "chars": (200, 100)},
        13: {"name": "8K", "chars": (240, 120)},
        14: {"name": "8K Max", "chars": (320, 160)}
    }

    # Teletext block graphics (mosaic patterns)
    TELETEXT_BLOCKS = {
        'full': '█', 'dark': '▓', 'medium': '▒', 'light': '░',
        'top': '▀', 'bottom': '▄', 'left': '▌', 'right': '▐',
        'topleft': '▘', 'topright': '▝', 'bottomleft': '▖', 'bottomright': '▗',
        'checkerboard': '▚', 'diagonal1': '▞', 'diagonal2': '▚',
        'upper_half': '▀', 'lower_half': '▄', 'left_half': '▌', 'right_half': '▐',
        'quarter1': '▘', 'quarter2': '▝', 'quarter3': '▖', 'quarter4': '▗',
        'shade1': '░', 'shade2': '▒', 'shade3': '▓', 'shade4': '█'
    }

    # Teletext color codes (ANSI escape sequences)
    TELETEXT_COLORS = {
        'black': '\033[30m', 'red': '\033[31m', 'green': '\033[32m',
        'yellow': '\033[33m', 'blue': '\033[34m', 'magenta': '\033[35m',
        'cyan': '\033[36m', 'white': '\033[37m',
        'bg_black': '\033[40m', 'bg_red': '\033[41m', 'bg_green': '\033[42m',
        'bg_yellow': '\033[43m', 'bg_blue': '\033[44m', 'bg_magenta': '\033[45m',
        'bg_cyan': '\033[46m', 'bg_white': '\033[47m',
        'reset': '\033[0m', 'bold': '\033[1m', 'dim': '\033[2m',
        'italic': '\033[3m', 'underline': '\033[4m', 'blink': '\033[5m',
        'reverse': '\033[7m', 'hidden': '\033[8m'
    }

    # Terrain patterns for maps
    TERRAIN_PATTERNS = {
        'ocean_deep': '█', 'ocean': '▓', 'ocean_shallow': '▒', 'coast': '░',
        'plains': '·', 'grassland': '≈', 'forest': '♠', 'jungle': '♣',
        'desert': '∴', 'tundra': '∙', 'ice': '❄',
        'hills': '∩', 'mountains': '▲', 'peaks': '▲',
        'urban': '▪', 'city': '■', 'metro': '●',
        'water': '≈', 'river': '~', 'lake': '○'
    }

    def __init__(self, **kwargs):
        """Initialize PanelCommandHandler, accepting kwargs for consistency with other handlers"""
        super().__init__()
        # Accept but ignore kwargs that other handlers use (theme, connection, etc.)
        self.panels = {}  # Store active panels
        self.default_tier = 7  # Desktop 80×40

    def handle(self, command, params, grid=None):
        """
        Handle PANEL commands.

        Syntax:
            PANEL CREATE <name> <width> <height> [tier]
            PANEL SHOW <name> [border]
            PANEL POKE <name> <x> <y> <char>
            PANEL WRITE <name> <x> <y> <text>
            PANEL FILL <name> <x> <y> <width> <height> <char>
            PANEL BLOCK <name> <x> <y> <block_type>
            PANEL PATTERN <name> <x> <y> <width> <height> <pattern>
            PANEL TERRAIN <name> <x> <y> <width> <height> <terrain>
            PANEL COLOR <name> <x> <y> <width> <height> <color>
            PANEL CLEAR <name>
            PANEL DELETE <name>
            PANEL LIST
            PANEL EMBED <name> <md_file>
            PANEL SIZE <tier>
            PANEL INFO [name]
            PANEL BLOCKS                  # List block types
            PANEL COLORS                  # List color codes
            PANEL TERRAINS                # List terrain patterns
        """
        if not params:
            return self._show_help()

        action = params[0].upper()

        if action == "CREATE":
            return self._create_panel(params[1:])
        elif action == "SHOW":
            return self._show_panel(params[1:])
        elif action == "POKE":
            return self._poke_panel(params[1:])
        elif action == "WRITE":
            return self._write_panel(params[1:])
        elif action == "FILL":
            return self._fill_panel(params[1:])
        elif action == "BLOCK":
            return self._block_panel(params[1:])
        elif action == "PATTERN":
            return self._pattern_panel(params[1:])
        elif action == "TERRAIN":
            return self._terrain_panel(params[1:])
        elif action == "COLOR":
            return self._color_panel(params[1:])
        elif action == "CLEAR":
            return self._clear_panel(params[1:])
        elif action == "DELETE":
            return self._delete_panel(params[1:])
        elif action == "LIST":
            return self._list_panels()
        elif action == "EMBED":
            return self._embed_panel(params[1:])
        elif action == "SIZE":
            return self._show_size_info(params[1:])
        elif action == "INFO":
            return self._panel_info(params[1:])
        elif action == "BLOCKS":
            return self._show_blocks()
        elif action == "COLORS":
            return self._show_colors()
        elif action == "TERRAINS":
            return self._show_terrains()
        else:
            return f"❌ Unknown PANEL action: {action}\n\n{self._show_help()}"

    def _create_panel(self, params):
        """Create a new teletext panel."""
        if len(params) < 3:
            return "❌ Usage: PANEL CREATE <name> <width> <height> [tier]\n\nExample: PANEL CREATE main 40 20 6"

        name = params[0]
        try:
            width = int(params[1])
            height = int(params[2])
            tier = int(params[3]) if len(params) > 3 else self.default_tier
        except ValueError:
            return "❌ Width, height, and tier must be numbers"

        if tier not in self.SCREEN_TIERS:
            return f"❌ Invalid tier: {tier}. Must be 0-14."

        # Validate dimensions against tier
        tier_info = self.SCREEN_TIERS[tier]
        max_w, max_h = tier_info["chars"]

        if width > max_w or height > max_h:
            return (f"⚠️  Panel {width}×{height} exceeds tier {tier} ({tier_info['name']}) "
                   f"maximum {max_w}×{max_h}\n"
                   f"💡 Use PANEL SIZE to see available tiers")

        # Create panel buffer
        buffer = [[' ' for _ in range(width)] for _ in range(height)]

        self.panels[name] = {
            'width': width,
            'height': height,
            'tier': tier,
            'buffer': buffer,
            'created': self._get_timestamp()
        }

        return (f"✅ Panel '{name}' created\n"
                f"   Size: {width}×{height} chars\n"
                f"   Tier: {tier} ({tier_info['name']})\n"
                f"   Max: {max_w}×{max_h}\n\n"
                f"💡 Use PANEL SHOW {name} to display")

    def _show_panel(self, params):
        """Display panel in teletext mode."""
        if not params:
            return "❌ Usage: PANEL SHOW <name> [border]"

        name = params[0]
        border = len(params) > 1 and params[1].lower() in ['true', 'yes', '1', 'border']

        if name not in self.panels:
            return f"❌ Panel '{name}' not found. Use PANEL LIST to see active panels."

        panel = self.panels[name]
        tier_info = self.SCREEN_TIERS[panel['tier']]

        output = []

        # Header
        output.append(f"╔{'═' * (panel['width'] + 2)}╗")
        output.append(f"║ Panel: {name} ({panel['width']}×{panel['height']}) - Tier {panel['tier']} ({tier_info['name']}) {'║'.rjust(panel['width'] - len(name) - len(str(panel['width'])) - len(str(panel['height'])) - 20)}")
        output.append(f"╠{'═' * (panel['width'] + 2)}╣")

        if border:
            # C64-style border
            output.append(f"║ {'▓' * panel['width']} ║")

        # Panel content
        for row in panel['buffer']:
            line = ''.join(row)
            if border:
                output.append(f"║ ▓{line}▓ ║")
            else:
                output.append(f"║ {line} ║")

        if border:
            output.append(f"║ {'▓' * panel['width']} ║")

        # Footer
        output.append(f"╚{'═' * (panel['width'] + 2)}╝")

        return '\n'.join(output)

    def _poke_panel(self, params):
        """POKE a character at x,y position (C64-style)."""
        if len(params) < 4:
            return "❌ Usage: PANEL POKE <name> <x> <y> <char>\n\nExample: PANEL POKE main 0 0 █"

        name = params[0]
        if name not in self.panels:
            return f"❌ Panel '{name}' not found"

        try:
            x = int(params[1])
            y = int(params[2])
            char = params[3][0] if params[3] else ' '
        except (ValueError, IndexError):
            return "❌ Invalid coordinates or character"

        panel = self.panels[name]

        if y < 0 or y >= panel['height'] or x < 0 or x >= panel['width']:
            return f"❌ Position ({x},{y}) out of bounds. Panel is {panel['width']}×{panel['height']}"

        panel['buffer'][y][x] = char

        return f"✅ POKE: '{char}' → ({x},{y}) in panel '{name}'"

    def _write_panel(self, params):
        """Write text to panel at x,y position."""
        if len(params) < 4:
            return "❌ Usage: PANEL WRITE <name> <x> <y> <text>\n\nExample: PANEL WRITE main 0 0 Hello uDOS!"

        name = params[0]
        if name not in self.panels:
            return f"❌ Panel '{name}' not found"

        try:
            x = int(params[1])
            y = int(params[2])
            text = ' '.join(params[3:])
        except ValueError:
            return "❌ Invalid coordinates"

        panel = self.panels[name]

        if y < 0 or y >= panel['height']:
            return f"❌ Y position {y} out of bounds (0-{panel['height']-1})"

        # Write text character by character
        for i, char in enumerate(text):
            if x + i >= panel['width']:
                break
            panel['buffer'][y][x + i] = char

        chars_written = min(len(text), panel['width'] - x)
        return f"✅ Wrote {chars_written} chars to panel '{name}' at ({x},{y})"

    def _fill_panel(self, params):
        """Fill rectangular area with character."""
        if len(params) < 6:
            return "❌ Usage: PANEL FILL <name> <x> <y> <width> <height> <char>\n\nExample: PANEL FILL main 0 0 10 5 █"

        name = params[0]
        if name not in self.panels:
            return f"❌ Panel '{name}' not found"

        try:
            x = int(params[1])
            y = int(params[2])
            width = int(params[3])
            height = int(params[4])
            char = params[5][0] if params[5] else ' '
        except (ValueError, IndexError):
            return "❌ Invalid parameters"

        panel = self.panels[name]
        count = 0

        for dy in range(height):
            for dx in range(width):
                px, py = x + dx, y + dy
                if 0 <= px < panel['width'] and 0 <= py < panel['height']:
                    panel['buffer'][py][px] = char
                    count += 1

        return f"✅ Filled {count} cells in panel '{name}'"

    def _block_panel(self, params):
        """Place teletext block at position."""
        if len(params) < 4:
            return "❌ Usage: PANEL BLOCK <name> <x> <y> <block_type>\n\nExample: PANEL BLOCK main 0 0 full\n\n💡 Use PANEL BLOCKS to see available types"

        name = params[0]
        if name not in self.panels:
            return f"❌ Panel '{name}' not found"

        try:
            x = int(params[1])
            y = int(params[2])
            block_type = params[3].lower()
        except (ValueError, IndexError):
            return "❌ Invalid parameters"

        if block_type not in self.TELETEXT_BLOCKS:
            return f"❌ Unknown block type: {block_type}\n\n💡 Use PANEL BLOCKS to see available types"

        char = self.TELETEXT_BLOCKS[block_type]
        panel = self.panels[name]

        if 0 <= x < panel['width'] and 0 <= y < panel['height']:
            panel['buffer'][y][x] = char
            return f"✅ Block '{block_type}' ({char}) placed at ({x},{y})"
        else:
            return f"❌ Position ({x},{y}) out of bounds"

    def _pattern_panel(self, params):
        """Fill area with repeating block pattern."""
        if len(params) < 6:
            return "❌ Usage: PANEL PATTERN <name> <x> <y> <width> <height> <pattern>\n\nExample: PANEL PATTERN main 0 0 20 10 checkerboard"

        name = params[0]
        if name not in self.panels:
            return f"❌ Panel '{name}' not found"

        try:
            x = int(params[1])
            y = int(params[2])
            width = int(params[3])
            height = int(params[4])
            pattern = params[5].lower()
        except (ValueError, IndexError):
            return "❌ Invalid parameters"

        panel = self.panels[name]
        count = 0

        # Define pattern sequences
        patterns = {
            'checkerboard': ['█', '░'],
            'gradient': ['█', '▓', '▒', '░'],
            'waves': ['≈', '~', '≈', '~'],
            'dots': ['·', ' '],
            'diagonal': ['▞', '▚']
        }

        if pattern not in patterns:
            # Try as single block type
            if pattern in self.TELETEXT_BLOCKS:
                char = self.TELETEXT_BLOCKS[pattern]
                for dy in range(height):
                    for dx in range(width):
                        px, py = x + dx, y + dy
                        if 0 <= px < panel['width'] and 0 <= py < panel['height']:
                            panel['buffer'][py][px] = char
                            count += 1
                return f"✅ Pattern filled {count} cells"
            else:
                return f"❌ Unknown pattern: {pattern}"

        pattern_seq = patterns[pattern]
        for dy in range(height):
            for dx in range(width):
                px, py = x + dx, y + dy
                if 0 <= px < panel['width'] and 0 <= py < panel['height']:
                    char_idx = (dx + dy) % len(pattern_seq)
                    panel['buffer'][py][px] = pattern_seq[char_idx]
                    count += 1

        return f"✅ Pattern '{pattern}' filled {count} cells"

    def _terrain_panel(self, params):
        """Fill area with terrain pattern."""
        if len(params) < 6:
            return "❌ Usage: PANEL TERRAIN <name> <x> <y> <width> <height> <terrain>\n\nExample: PANEL TERRAIN main 0 0 20 10 ocean\n\n💡 Use PANEL TERRAINS to see available types"

        name = params[0]
        if name not in self.panels:
            return f"❌ Panel '{name}' not found"

        try:
            x = int(params[1])
            y = int(params[2])
            width = int(params[3])
            height = int(params[4])
            terrain = params[5].lower()
        except (ValueError, IndexError):
            return "❌ Invalid parameters"

        if terrain not in self.TERRAIN_PATTERNS:
            return f"❌ Unknown terrain type: {terrain}\n\n💡 Use PANEL TERRAINS to see available types"

        char = self.TERRAIN_PATTERNS[terrain]
        panel = self.panels[name]
        count = 0

        for dy in range(height):
            for dx in range(width):
                px, py = x + dx, y + dy
                if 0 <= px < panel['width'] and 0 <= py < panel['height']:
                    panel['buffer'][py][px] = char
                    count += 1

        return f"✅ Terrain '{terrain}' ({char}) filled {count} cells"

    def _color_panel(self, params):
        """Apply color to panel area (for terminal display)."""
        if len(params) < 6:
            return "❌ Usage: PANEL COLOR <name> <x> <y> <width> <height> <color>\n\nExample: PANEL COLOR main 0 0 20 10 red\n\n💡 Use PANEL COLORS to see available colors"

        # Note: This sets metadata for color rendering in SHOW
        # Actual ANSI color application happens in _show_panel
        name = params[0]
        if name not in self.panels:
            return f"❌ Panel '{name}' not found"

        try:
            x = int(params[1])
            y = int(params[2])
            width = int(params[3])
            height = int(params[4])
            color = params[5].lower()
        except (ValueError, IndexError):
            return "❌ Invalid parameters"

        if color not in self.TELETEXT_COLORS:
            return f"❌ Unknown color: {color}\n\n💡 Use PANEL COLORS to see available colors"

        panel = self.panels[name]
        if 'colors' not in panel:
            panel['colors'] = {}

        # Store color region
        region_key = f"{x},{y},{width},{height}"
        panel['colors'][region_key] = color

        return f"✅ Color '{color}' applied to region ({x},{y}) {width}×{height}"

    def _show_blocks(self):
        """Display available teletext blocks."""
        output = ["📦 Teletext Block Graphics:\n"]
        output.append("Basic Blocks:")
        output.append(f"  full={self.TELETEXT_BLOCKS['full']}  dark={self.TELETEXT_BLOCKS['dark']}  medium={self.TELETEXT_BLOCKS['medium']}  light={self.TELETEXT_BLOCKS['light']}")
        output.append("\nHalf Blocks:")
        output.append(f"  top={self.TELETEXT_BLOCKS['top']}  bottom={self.TELETEXT_BLOCKS['bottom']}  left={self.TELETEXT_BLOCKS['left']}  right={self.TELETEXT_BLOCKS['right']}")
        output.append("\nQuarter Blocks:")
        output.append(f"  topleft={self.TELETEXT_BLOCKS['topleft']}  topright={self.TELETEXT_BLOCKS['topright']}  bottomleft={self.TELETEXT_BLOCKS['bottomleft']}  bottomright={self.TELETEXT_BLOCKS['bottomright']}")
        output.append("\nPatterns:")
        output.append(f"  checkerboard={self.TELETEXT_BLOCKS['checkerboard']}  diagonal1={self.TELETEXT_BLOCKS['diagonal1']}")
        output.append("\n💡 Usage: PANEL BLOCK <name> <x> <y> <type>")
        return '\n'.join(output)

    def _show_colors(self):
        """Display available colors."""
        output = ["🎨 Teletext Colors:\n"]
        output.append("Foreground:")
        output.append("  black, red, green, yellow, blue, magenta, cyan, white")
        output.append("\nBackground:")
        output.append("  bg_black, bg_red, bg_green, bg_yellow, bg_blue, bg_magenta, bg_cyan, bg_white")
        output.append("\nEffects:")
        output.append("  bold, dim, italic, underline, blink, reverse, hidden")
        output.append("\n💡 Usage: PANEL COLOR <name> <x> <y> <width> <height> <color>")
        return '\n'.join(output)

    def _show_terrains(self):
        """Display available terrain types."""
        output = ["🗺️  Terrain Patterns:\n"]
        output.append("Water:")
        for t in ['ocean_deep', 'ocean', 'ocean_shallow', 'coast', 'water', 'river', 'lake']:
            if t in self.TERRAIN_PATTERNS:
                output.append(f"  {t}={self.TERRAIN_PATTERNS[t]}")
        output.append("\nLand:")
        for t in ['plains', 'grassland', 'forest', 'jungle', 'desert', 'tundra', 'ice']:
            if t in self.TERRAIN_PATTERNS:
                output.append(f"  {t}={self.TERRAIN_PATTERNS[t]}")
        output.append("\nElevation:")
        for t in ['hills', 'mountains', 'peaks']:
            if t in self.TERRAIN_PATTERNS:
                output.append(f"  {t}={self.TERRAIN_PATTERNS[t]}")
        output.append("\nUrban:")
        for t in ['urban', 'city', 'metro']:
            if t in self.TERRAIN_PATTERNS:
                output.append(f"  {t}={self.TERRAIN_PATTERNS[t]}")
        output.append("\n💡 Usage: PANEL TERRAIN <name> <x> <y> <width> <height> <terrain>")
        return '\n'.join(output)

    def _clear_panel(self, params):
        """Clear panel buffer."""
        if not params:
            return "❌ Usage: PANEL CLEAR <name>"

        name = params[0]
        if name not in self.panels:
            return f"❌ Panel '{name}' not found"

        panel = self.panels[name]
        panel['buffer'] = [[' ' for _ in range(panel['width'])] for _ in range(panel['height'])]

        return f"✅ Panel '{name}' cleared"

    def _delete_panel(self, params):
        """Delete panel."""
        if not params:
            return "❌ Usage: PANEL DELETE <name>"

        name = params[0]
        if name not in self.panels:
            return f"❌ Panel '{name}' not found"

        del self.panels[name]
        return f"✅ Panel '{name}' deleted"

    def _list_panels(self):
        """List all active panels."""
        if not self.panels:
            return "📋 No active panels\n\n💡 Create one with: PANEL CREATE <name> <width> <height>"

        output = ["📋 Active Panels:\n"]
        for name, panel in self.panels.items():
            tier_info = self.SCREEN_TIERS[panel['tier']]
            output.append(f"  • {name}: {panel['width']}×{panel['height']} (Tier {panel['tier']} - {tier_info['name']})")

        output.append(f"\n💡 Use PANEL SHOW <name> to display")
        return '\n'.join(output)

    def _embed_panel(self, params):
        """Embed panel in markdown file."""
        if len(params) < 2:
            return "❌ Usage: PANEL EMBED <name> <md_file>"

        name = params[0]
        md_file = params[1]

        if name not in self.panels:
            return f"❌ Panel '{name}' not found"

        panel = self.panels[name]

        # Generate markdown code block
        md_content = ["```"]
        for row in panel['buffer']:
            md_content.append(''.join(row))
        md_content.append("```")

        # Append to markdown file
        try:
            md_path = Path(md_file)
            with open(md_path, 'a', encoding='utf-8') as f:
                f.write(f"\n\n## Panel: {name}\n\n")
                f.write('\n'.join(md_content))
                f.write('\n')

            return f"✅ Panel '{name}' embedded in {md_file}"
        except Exception as e:
            return f"❌ Error embedding panel: {str(e)}"

    def _show_size_info(self, params):
        """Show screen tier size information."""
        if params:
            try:
                tier = int(params[0])
                if tier not in self.SCREEN_TIERS:
                    return f"❌ Invalid tier: {tier}. Must be 0-14."

                info = self.SCREEN_TIERS[tier]
                w, h = info['chars']
                return (f"📐 Tier {tier}: {info['name']}\n"
                       f"   Max Size: {w}×{h} characters\n"
                       f"   Total: {w * h:,} characters")
            except ValueError:
                return "❌ Tier must be a number (0-14)"

        # Show all tiers
        output = ["📐 Screen Tier Sizes (characters):\n"]
        for tier, info in self.SCREEN_TIERS.items():
            w, h = info['chars']
            output.append(f"  Tier {tier:2d}: {w:3d}×{h:3d} - {info['name']}")

        return '\n'.join(output)

    def _panel_info(self, params):
        """Show panel information."""
        if not params:
            return self._list_panels()

        name = params[0]
        if name not in self.panels:
            return f"❌ Panel '{name}' not found"

        panel = self.panels[name]
        tier_info = self.SCREEN_TIERS[panel['tier']]
        max_w, max_h = tier_info['chars']

        # Count non-space characters
        char_count = sum(1 for row in panel['buffer'] for c in row if c != ' ')
        total_cells = panel['width'] * panel['height']
        fill_percent = (char_count / total_cells * 100) if total_cells > 0 else 0

        return (f"📋 Panel Info: {name}\n"
               f"   Size: {panel['width']}×{panel['height']} chars\n"
               f"   Total Cells: {total_cells:,}\n"
               f"   Used Cells: {char_count:,} ({fill_percent:.1f}%)\n"
               f"   Tier: {panel['tier']} ({tier_info['name']})\n"
               f"   Tier Max: {max_w}×{max_h}\n"
               f"   Created: {panel['created']}")

    def _show_help(self):
        """Show PANEL command help."""
        return """📐 PANEL Command - Teletext Display Control

Basic Commands:
  PANEL CREATE <name> <width> <height> [tier]  Create panel
  PANEL SHOW <name> [border]                   Display panel
  PANEL POKE <name> <x> <y> <char>             Write character
  PANEL WRITE <name> <x> <y> <text>            Write text
  PANEL CLEAR <name>                           Clear panel
  PANEL DELETE <name>                          Delete panel
  PANEL LIST                                   List panels
  PANEL INFO [name]                            Panel information

Teletext Graphics:
  PANEL FILL <name> <x> <y> <w> <h> <char>     Fill area with char
  PANEL BLOCK <name> <x> <y> <type>            Place block graphic
  PANEL PATTERN <name> <x> <y> <w> <h> <pat>   Fill with pattern
  PANEL TERRAIN <name> <x> <y> <w> <h> <type>  Fill with terrain
  PANEL COLOR <name> <x> <y> <w> <h> <color>   Apply color
  PANEL BLOCKS                                 List block types
  PANEL COLORS                                 List colors
  PANEL TERRAINS                               List terrain types

Advanced:
  PANEL EMBED <name> <md_file>                 Embed in markdown
  PANEL SIZE [tier]                            Show tier sizes

Examples:
  PANEL CREATE map 480 270 14                  Create world map
  PANEL TERRAIN map 0 0 480 100 ocean          Fill ocean area
  PANEL BLOCK map 240 135 city                 Mark city location
  PANEL PATTERN map 100 150 50 20 gradient    Gradient pattern
  PANEL SHOW map                               Display map
  PANEL EMBED map data/maps/world.md           Embed in markdown

Block Types: full, dark, medium, light, top, bottom, left, right
Patterns: checkerboard, gradient, waves, dots, diagonal
Terrains: ocean, coast, plains, forest, desert, mountains, city
Colors: red, green, blue, yellow, cyan, magenta, white, bg_*

💡 Use PANEL BLOCKS/COLORS/TERRAINS for complete lists
"""

    def _get_timestamp(self):
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
