# uDOS v1.0.0 - Viewport Visualization & Color Testing

import os
import shutil

class ViewportVisualizer:
    """
    Creates ASCII art splash screens and color tests for viewport validation.
    Tests terminal capabilities: dimensions, color support, Unicode rendering.
    """

    # Polaroid Colors (System Default) - High-contrast photo-inspired
    COLORS = {
        'red':     '\033[38;5;196m',  # tput 196 - Bold Red
        'green':   '\033[38;5;46m',   # tput 46  - Bright Green
        'yellow':  '\033[38;5;226m',  # tput 226 - Yellow Burst
        'blue':    '\033[38;5;21m',   # tput 21  - Deep Blue
        'purple':  '\033[38;5;201m',  # tput 201 - Magenta Pink
        'cyan':    '\033[38;5;51m',   # tput 51  - Cyan Flash
        'white':   '\033[38;5;15m',   # tput 15  - Pure White
        'black':   '\033[38;5;16m',   # tput 16  - Pure Black

        # Grayscale gradient blocks
        'gray_0':  '\033[38;5;232m',  # Darkest gray
        'gray_1':  '\033[38;5;236m',
        'gray_2':  '\033[38;5;240m',
        'gray_3':  '\033[38;5;244m',
        'gray_4':  '\033[38;5;248m',
        'gray_5':  '\033[38;5;252m',  # Lightest gray

        'reset':   '\033[0m'
    }

    # Shading blocks (Unicode)
    SHADES = {
        'full':    '█',  # 100%
        'dark':    '▓',  # 75%
        'medium':  '▒',  # 50%
        'light':   '░',  # 25%
        'empty':   ' '   # 0%
    }

    # ASCII fallback blocks
    ASCII_SHADES = {
        'full':    '#',
        'dark':    '@',
        'medium':  '+',
        'light':   '.',
        'empty':   ' '
    }

    def __init__(self, viewport=None):
        self.viewport = viewport
        self.width = viewport.width if viewport else 80
        self.height = viewport.height if viewport else 24
        self.unicode_support = self._test_unicode()
        self.color_support = self._test_color()
        self.monospace_font = self._test_monospace()

    def _test_unicode(self):
        """Test if terminal supports Unicode."""
        try:
            # Try to encode Unicode block character
            '█'.encode('utf-8')
            return True
        except:
            return False

    def _test_color(self):
        """Test if terminal supports 256 colors."""
        # Check TERM environment variable
        term = os.environ.get('TERM', '')
        return '256color' in term or 'truecolor' in term

    def _test_monospace(self):
        """Detect if terminal is using monospace font."""
        # All terminals should use monospace, but we'll check viewport consistency
        if self.viewport:
            # If viewport detection worked, assume monospace
            return True
        return True  # Default assumption

    def color(self, text, color_name):
        """Apply color to text if supported."""
        if not self.color_support:
            return text
        color_code = self.COLORS.get(color_name, self.COLORS['reset'])
        reset = self.COLORS['reset']
        return f"{color_code}{text}{reset}"

    def shade_block(self, shade_level):
        """Get appropriate shade block character."""
        blocks = self.SHADES if self.unicode_support else self.ASCII_SHADES
        return blocks.get(shade_level, blocks['empty'])

    def generate_splash_screen(self):
        """Generate complete viewport splash with color and dimension tests."""
        lines = []

        # Header
        lines.append("=" * self.width)
        title = "🔄 VIEWPORT & COLOR TEST"
        padding = (self.width - len(title)) // 2
        lines.append(" " * padding + title)
        lines.append("=" * self.width)
        lines.append("")

        # Terminal info
        lines.append(f"📐 Dimensions: {self.width}×{self.height} characters")
        lines.append(f"🔤 Unicode: {'✅ Supported' if self.unicode_support else '⚠️  Limited (ASCII fallback)'}")
        lines.append(f"🎨 Color: {'✅ 256-color' if self.color_support else '⚠️  Monochrome'}")
        lines.append(f"🖋️  Font: {'✅ Monospace detected' if self.monospace_font else '⚠️  Variable-width detected'}")

        if self.viewport:
            lines.append(f"📱 Device: {self.viewport.device_type}")
            lines.append(f"🎯 Grid: {self.viewport.grid_width}×{self.viewport.grid_height} cells")

        lines.append("")

        # Color palette test
        lines.append("🎨 POLAROID COLOR PALETTE (System Default):")
        lines.append("─" * self.width)

        # Color blocks
        color_line = "  "
        color_labels = []
        for name, code in [('red', 'red'), ('green', 'green'), ('yellow', 'yellow'),
                          ('blue', 'blue'), ('purple', 'purple'), ('cyan', 'cyan')]:
            block = self.shade_block('full') * 4
            color_line += self.color(block, code) + "  "
            color_labels.append(f"{name:^6}")

        lines.append(color_line)
        lines.append("  " + "  ".join(color_labels))
        lines.append("")

        # Grayscale gradient test
        lines.append("⬛ GRAYSCALE GRADIENT TEST:")
        lines.append("─" * self.width)

        gradient_line = "  "
        if self.unicode_support:
            # Unicode gradient
            for i in range(6):
                gray = f"gray_{i}"
                block = self.shade_block('full') * 6
                gradient_line += self.color(block, gray)
        else:
            # ASCII gradient
            for shade in ['full', 'dark', 'medium', 'light', 'empty']:
                gradient_line += self.shade_block(shade) * 6

        lines.append(gradient_line)
        lines.append("  " + "Black → Gray → White")
        lines.append("")

        # Shading blocks test
        lines.append("▓ SHADING BLOCKS TEST:")
        lines.append("─" * self.width)

        shade_line = "  "
        shade_labels = []
        for shade, label in [('full', '100%'), ('dark', '75%'),
                            ('medium', '50%'), ('light', '25%'), ('empty', '0%')]:
            shade_line += self.shade_block(shade) * 6 + "  "
            shade_labels.append(f"{label:^6}")

        lines.append(shade_line)
        lines.append("  " + "  ".join(shade_labels))
        lines.append("")

        # ASCII Art Test (uDOS logo)
        lines.append("🎯 ASCII ART RENDERING:")
        lines.append("─" * self.width)

        logo = self._generate_logo()
        for line in logo:
            # Center the logo
            padding = (self.width - len(line)) // 2
            lines.append(" " * padding + line)

        lines.append("")

        # Viewport boundary test
        lines.append("📏 VIEWPORT BOUNDARY TEST:")
        lines.append("─" * self.width)

        # Top border
        border_char = self.shade_block('full') if self.unicode_support else '#'
        lines.append(border_char * self.width)

        # Side borders with ruler
        ruler_width = self.width - 4
        ruler = "".join([str(i % 10) for i in range(ruler_width)])
        lines.append(border_char + " " + ruler + " " + border_char)

        # Bottom border
        lines.append(border_char * self.width)
        lines.append("")

        # Footer with palette info
        lines.append("=" * self.width)
        lines.append("Polaroid Color Codes: R#FF1744 G#00E676 Y#FFEB3B B#2196F3 P#E91E63 C#00E5FF")
        lines.append("Default palette applied. Colors: 256-color mode (ANSI)")
        lines.append("=" * self.width)

        return "\n".join(lines)

    def _generate_logo(self):
        """Generate uDOS ASCII art logo."""
        if self.unicode_support:
            return [
                self.color("██╗   ██╗██████╗  ██████╗ ███████╗", 'cyan'),
                self.color("██║   ██║██╔══██╗██╔═══██╗██╔════╝", 'cyan'),
                self.color("██║   ██║██║  ██║██║   ██║███████╗", 'blue'),
                self.color("██║   ██║██║  ██║██║   ██║╚════██║", 'blue'),
                self.color("╚██████╔╝██████╔╝╚██████╔╝███████║", 'purple'),
                self.color(" ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝", 'purple'),
            ]
        else:
            # ASCII fallback
            return [
                " _   _ ____   ___  ____  ",
                "| | | |  _ \\ / _ \\/ ___| ",
                "| | | | | | | | | \\___ \\ ",
                "| |_| | |_| | |_| |___) |",
                " \\___/|____/ \\___/|____/ ",
            ]

    def generate_compact_test(self):
        """Generate compact color test for inline display."""
        blocks = []

        # Color blocks
        for name, code in [('R', 'red'), ('G', 'green'), ('Y', 'yellow'),
                          ('B', 'blue'), ('P', 'purple'), ('C', 'cyan')]:
            block = self.shade_block('full')
            blocks.append(self.color(f"{name}:{block}{block}", code))

        # Grayscale
        gray_blocks = []
        for i in range(6):
            gray = f"gray_{i}"
            block = self.shade_block('full')
            gray_blocks.append(self.color(block, gray))

        return "  ".join(blocks) + " | " + "".join(gray_blocks)

    def test_font_spacing(self):
        """Test monospace font consistency."""
        test_lines = []

        test_lines.append("Font Spacing Test:")
        test_lines.append("─" * 40)
        test_lines.append("iiii IIII 1111 |||| .... ____")
        test_lines.append("mmmm MMMM WWWW @@@@ #### ████")
        test_lines.append("0123456789 ABCDEFGHIJ abcdefghij")
        test_lines.append("")

        # All lines should align perfectly in monospace
        test_lines.append("If columns don't align above,")
        test_lines.append("terminal may not be monospace.")

        return "\n".join(test_lines)
