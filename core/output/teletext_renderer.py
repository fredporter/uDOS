#!/usr/bin/env python3
"""
uDOS v1.0.4 - Teletext Web Renderer

Generates teletext-style HTML/CSS output for mapping data using mosaic block art.
Based on galax.xyz/TELETEXT/ style and teletext mono starter framework.

Features:
- Mosaic character rendering (2x3 pixel blocks)
- WST color palette support
- Contiguous/separated mosaic modes
- Double-height text support
- Interactive scaling and controls
- Cell-based grid layout for maps

Version: 1.0.4
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import sys
import math

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))


class TeletextMosaicRenderer:
    """Renders maps and data using teletext mosaic block art."""

    # WST color palette
    COLORS = {
        'BLACK': ('blk', '#000'),
        'RED': ('red', '#F00'),
        'GREEN': ('grn', '#0F0'),
        'YELLOW': ('yel', '#FF0'),
        'BLUE': ('blu', '#00F'),
        'MAGENTA': ('mag', '#F0F'),
        'CYAN': ('cyn', '#0FF'),
        'WHITE': ('wht', '#FFF')
    }

    # Mosaic character mappings (2x3 pixel blocks)
    # Bit order: TL, TR, ML, MR, BL, BR (Top-Left, Top-Right, etc.)
    MOSAIC_CHARS = {
        # Basic shapes
        'EMPTY': (0x0000, '&#xE200;'),      # 000000
        'FULL': (0x003F, '&#xE23F;'),       # 111111
        'TOP_HALF': (0x0003, '&#xE203;'),   # 110000
        'BOTTOM_HALF': (0x0030, '&#xE230;'), # 001100
        'LEFT_HALF': (0x0015, '&#xE215;'),  # 101010
        'RIGHT_HALF': (0x002A, '&#xE22A;'), # 010101
        'CORNERS': (0x0033, '&#xE233;'),    # 110011
        'SIDES': (0x000C, '&#xE20C;'),      # 001100
    }

    def __init__(self):
        """Initialize teletext renderer with mosaic character data."""
        self.mosaic_data = self._load_mosaic_data()
        self.font_loaded = False

    def _load_mosaic_data(self) -> Dict[int, str]:
        """Load mosaic character mappings from CSV data."""
        mosaic_map = {}

        # Generate all 64 possible 2x3 mosaic combinations
        for i in range(64):
            # Convert to 6-bit pattern (TL, TR, ML, MR, BL, BR)
            bits = format(i, '06b')
            # Map to Unicode private use area (E200-E23F for contiguous)
            codepoint = 0xE200 + i
            html_entity = f'&#x{codepoint:04X};'
            mosaic_map[i] = html_entity

        return mosaic_map

    def generate_map_html(self, map_data: List[List[str]],
                         title: str = "uDOS Teletext Map",
                         width: int = 40, height: int = 24) -> str:
        """
        Generate complete HTML page with teletext map rendering.

        Args:
            map_data: 2D array of map symbols
            title: Page title
            width: Teletext grid width (characters)
            height: Teletext grid height (characters)

        Returns:
            Complete HTML page as string
        """

        # Convert map data to teletext grid
        teletext_grid = self._convert_map_to_teletext(map_data, width, height)

        html = f'''<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <title>{title}</title>
    <style>{self._get_teletext_css()}</style>
</head>
<body class="tt-bg-blk tt-fg-wht" style="margin:16px">
    <h1 style="font-family: var(--mono);">{title}</h1>

    <div class="teletext tt-bg-blk tt-fg-wht" id="page" style="--cols: {width}; --rows: {height};">
        {teletext_grid}
    </div>

    <section style="margin-top:24px; font-family: var(--mono);">
        <button onclick="toggleMode()">Toggle Mosaic Mode</button>
        <button onclick="setScale(1)">1×</button>
        <button onclick="setScale(2)">2×</button>
        <button onclick="setScale(3)">3×</button>
        <button onclick="setScale(4)">4×</button>
        <button onclick="exportMap()">Export Map</button>
    </section>

    <script>{self._get_teletext_js()}</script>
</body>
</html>'''

        return html

    def _convert_map_to_teletext(self, map_data: List[List[str]],
                                width: int, height: int) -> str:
        """Convert ASCII map data to teletext mosaic representation."""
        grid_html = []

        # Resize map data to fit teletext grid
        resized_map = self._resize_map_data(map_data, width, height)

        for row_idx, row in enumerate(resized_map):
            for col_idx, char in enumerate(row):
                cell_html = self._char_to_teletext_cell(char, row_idx, col_idx)
                grid_html.append(cell_html)

        return '\n        '.join(grid_html)

    def _resize_map_data(self, map_data: List[List[str]],
                        target_width: int, target_height: int) -> List[List[str]]:
        """Resize map data to fit target dimensions."""
        if not map_data:
            return [[' ' for _ in range(target_width)] for _ in range(target_height)]

        original_height = len(map_data)
        original_width = len(map_data[0]) if map_data else 0

        resized = []
        for y in range(target_height):
            row = []
            for x in range(target_width):
                # Sample from original map data with scaling
                orig_y = int(y * original_height / target_height)
                orig_x = int(x * original_width / target_width)

                if orig_y < len(map_data) and orig_x < len(map_data[orig_y]):
                    char = map_data[orig_y][orig_x]
                else:
                    char = ' '

                row.append(char)
            resized.append(row)

        return resized

    def _char_to_teletext_cell(self, char: str, row: int, col: int) -> str:
        """Convert a single character to teletext cell HTML."""

        # Color mapping based on character type
        color_class = "tt-fg-wht"  # Default white
        mosaic_pattern = None

        if char == '◉':  # Current position
            color_class = "tt-fg-yel tt-flash"
            mosaic_pattern = self.MOSAIC_CHARS['FULL'][1]
        elif char == 'M':  # MEGA city
            color_class = "tt-fg-red"
            mosaic_pattern = self.MOSAIC_CHARS['FULL'][1]
        elif char == 'C':  # MAJOR city
            color_class = "tt-fg-grn"
            mosaic_pattern = self.MOSAIC_CHARS['CORNERS'][1]
        elif char == '•':  # Minor settlement
            color_class = "tt-fg-cyn"
            mosaic_pattern = self.MOSAIC_CHARS['TOP_HALF'][1]
        elif char == '~':  # Water/ocean
            color_class = "tt-fg-blu"
            # Create wave pattern based on position
            wave_pattern = (col + row) % 4
            if wave_pattern == 0:
                mosaic_pattern = '&#xE20A;'  # 010100
            elif wave_pattern == 1:
                mosaic_pattern = '&#xE205;'  # 101000
            elif wave_pattern == 2:
                mosaic_pattern = '&#xE214;'  # 001010
            else:
                mosaic_pattern = '&#xE201;'  # 100000
        elif char == '.':  # Land/terrain
            color_class = "tt-fg-grn"
            # Create terrain pattern
            terrain_pattern = (col * 3 + row * 7) % 8
            patterns = ['&#xE201;', '&#xE204;', '&#xE210;', '&#xE208;',
                       '&#xE202;', '&#xE212;', '&#xE220;', '&#xE211;']
            mosaic_pattern = patterns[terrain_pattern]
        elif char == 'S':  # Sydney (example city marker)
            color_class = "tt-fg-mag"
            mosaic_pattern = self.MOSAIC_CHARS['CORNERS'][1]
        else:
            # Regular character or space
            if char == ' ':
                mosaic_pattern = self.MOSAIC_CHARS['EMPTY'][1]
            else:
                # For text characters, use direct character
                return f'<span class="cell {color_class}">{char}</span>'

        return f'<span class="cell {color_class} tt-con">{mosaic_pattern}</span>'

    def _get_teletext_css(self) -> str:
        """Generate teletext CSS styling."""
        return '''
        :root{
            --mono: Menlo, SFMono-Regular, ui-monospace,
                    "DejaVu Sans Mono","Liberation Mono",
                    Consolas,"Courier New",monospace;
        }

        @font-face{
            font-family: "TT-Mosaic";
            src: url("data:font/woff2;base64,") format("woff2");
            font-weight: 400;
            font-style: normal;
            font-display: swap;
        }

        .mono, .teletext{
            font-family: "TT-Mosaic", var(--mono);
            font-feature-settings: "tnum" 1, "liga" 0;
        }

        .teletext {
            --cols: 40;
            --rows: 24;
            --cell: 1ch;
            --lhpx: 16px;
            display: grid;
            grid-template-columns: repeat(var(--cols), var(--cell));
            grid-auto-rows: var(--lhpx);
            font-size: 16px;
            line-height: var(--lhpx);
            letter-spacing: 0;
            white-space: pre;
            background: #000;
            color: #FFF;
            border: 2px solid #333;
            padding: 8px;
        }

        .teletext .cell {
            width: 1ch;
            height: var(--lhpx);
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .teletext.scale-2 { transform: scale(2); transform-origin: top left; }
        .teletext.scale-3 { transform: scale(3); transform-origin: top left; }
        .teletext.scale-4 { transform: scale(4); transform-origin: top left; }

        /* WST Color Palette */
        .tt-fg-blk{ color:#000; } .tt-fg-red{ color:#F00; } .tt-fg-grn{ color:#0F0; }
        .tt-fg-yel{ color:#FF0; } .tt-fg-blu{ color:#00F; } .tt-fg-mag{ color:#F0F; }
        .tt-fg-cyn{ color:#0FF; } .tt-fg-wht{ color:#FFF; }
        .tt-bg-blk{ background:#000; } .tt-bg-blu{ background:#00F; } .tt-bg-red{ background:#F00; }
        .tt-bg-grn{ background:#0F0; } .tt-bg-yel{ background:#FF0; } .tt-bg-mag{ background:#F0F; }
        .tt-bg-cyn{ background:#0FF; } .tt-bg-wht{ background:#FFF; }

        /* Mosaic modes */
        .tt-con{ font-feature-settings: "ss01" 0; }
        .tt-sep{ font-feature-settings: "ss01" 1; }

        /* Double-height */
        .tt-dblh{ line-height: calc(2 * var(--lhpx)); }

        /* Flashing */
        @keyframes tt-flash { 0%, 49% { opacity:1 } 50%, 100% { opacity:0 } }
        .tt-flash{ animation: tt-flash 1s step-end infinite; }

        /* Additional styling for map elements */
        .map-title {
            color: #FF0;
            font-weight: bold;
            grid-column: 1 / -1;
            text-align: center;
            margin-bottom: 8px;
        }

        .map-legend {
            grid-column: 1 / -1;
            font-size: 12px;
            margin-top: 8px;
            color: #CCC;
        }
        '''

    def _get_teletext_js(self) -> str:
        """Generate teletext JavaScript controls."""
        return '''
        function toggleMode() {
            const root = document.querySelector('.teletext');
            if (root.classList.contains('tt-con')) {
                root.classList.remove('tt-con');
                root.classList.add('tt-sep');
            } else {
                root.classList.remove('tt-sep');
                root.classList.add('tt-con');
            }
        }

        function setScale(scale) {
            const root = document.querySelector('.teletext');
            root.classList.remove('scale-2', 'scale-3', 'scale-4');
            if (scale > 1) {
                root.classList.add(`scale-${scale}`);
            }
        }

        function exportMap() {
            const mapData = document.querySelector('.teletext').outerHTML;
            const blob = new Blob([mapData], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'udos-teletext-map.html';
            a.click();
            URL.revokeObjectURL(url);
        }

        // Auto-fit map to container
        function autoFit() {
            const container = document.querySelector('.teletext');
            const parent = container.parentElement;
            const scale = Math.min(
                parent.clientWidth / container.scrollWidth,
                parent.clientHeight / container.scrollHeight
            );

            if (scale < 1) {
                container.style.transform = `scale(${scale})`;
                container.style.transformOrigin = 'top left';
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            autoFit();
            window.addEventListener('resize', autoFit);
        });
        '''

    def generate_map_page(self, map_ascii: str, title: str = "uDOS Map",
                         cell_info: Optional[Dict] = None) -> str:
        """
        Generate a complete teletext map page from ASCII map data.

        Args:
            map_ascii: ASCII art map string
            title: Page title
            cell_info: Optional cell information to display

        Returns:
            Complete HTML page
        """

        # Parse ASCII map into 2D array
        lines = map_ascii.strip().split('\n')
        map_data = [list(line) for line in lines]

        # Generate base HTML
        html = self.generate_map_html(map_data, title)

        # Add cell information if provided
        if cell_info:
            info_section = self._generate_info_section(cell_info)
            html = html.replace('</body>', f'{info_section}</body>')

        return html

    def _generate_info_section(self, cell_info: Dict) -> str:
        """Generate information section for map page."""
        return f'''
    <section style="margin-top:24px; font-family: var(--mono); color: #FFF;">
        <h3 style="color: #FF0;">Map Information</h3>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
            <div>
                <h4 style="color: #0FF;">Location</h4>
                <p>Cell: {cell_info.get('cell_ref', 'N/A')}</p>
                <p>Coordinates: {cell_info.get('coordinates', 'N/A')}</p>
                <p>City: {cell_info.get('city_name', 'None')}</p>
            </div>
            <div>
                <h4 style="color: #0FF;">Legend</h4>
                <p><span style="color: #FF0;">◉</span> Current Position</p>
                <p><span style="color: #F00;">■</span> MEGA City</p>
                <p><span style="color: #0F0;">▄</span> MAJOR City</p>
                <p><span style="color: #00F;">~</span> Water/Ocean</p>
                <p><span style="color: #0F0;">.</span> Land/Terrain</p>
            </div>
        </div>
    </section>
        '''


class TeletextMapIntegration:
    """Integration layer between uDOS mapping system and teletext renderer."""

    def __init__(self):
        """Initialize teletext map integration."""
        self.renderer = TeletextMosaicRenderer()

    def render_map_as_teletext(self, map_engine, center_cell: str,
                              width: int = 40, height: int = 20) -> str:
        """
        Render a map using teletext mosaic art.

        Args:
            map_engine: IntegratedMapEngine instance
            center_cell: Cell reference for map center
            width: Map width in characters
            height: Map height in characters

        Returns:
            Complete HTML page with teletext map
        """

        # Generate ASCII map from engine
        ascii_map = map_engine.generate_ascii_map(center_cell, width, height)

        # Get cell information
        try:
            bounds = map_engine.cell_system.get_cell_bounds(center_cell)
            city = map_engine.get_city_by_cell(center_cell)

            cell_info = {
                'cell_ref': center_cell,
                'coordinates': f"{bounds['lat_center']:.2f}°, {bounds['lon_center']:.2f}°",
                'city_name': city['name'] if city else 'Open Area'
            }
        except:
            cell_info = {
                'cell_ref': center_cell,
                'coordinates': 'Unknown',
                'city_name': 'Unknown'
            }

        # Generate teletext page
        title = f"uDOS Map - Cell {center_cell}"
        return self.renderer.generate_map_page(ascii_map, title, cell_info)

    def save_teletext_map(self, html_content: str, filename: str = None) -> str:
        """Save teletext map to HTML file."""
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"udos_teletext_map_{timestamp}.html"

        # Ensure output directory exists
        output_dir = Path("output/teletext")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(filepath)


if __name__ == "__main__":
    # Test teletext renderer
    print("🖥️  Testing Teletext Renderer")
    print("=" * 40)

    # Create test map data
    test_map = [
        "~..~..~..~..~..~..~..~..~..~",
        ".                          .",
        "~                          ~",
        ".          ◉               .",
        "~                          ~",
        ".                         S.",
        "~..~..~..~..~..~..~..~..~..~"
    ]

    renderer = TeletextMosaicRenderer()
    html_output = renderer.generate_map_html(test_map, "Test Map", 30, 10)

    # Save test output
    output_dir = Path("output/teletext")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "test_teletext_map.html", 'w') as f:
        f.write(html_output)

    print("✅ Teletext renderer test complete")
    print(f"📄 Test output saved to: {output_dir / 'test_teletext_map.html'}")
    print("🌐 Open in browser to view teletext map!")
