# uDOS v1.0.0 - Viewport Detection System
# Integrates with DISPLAY-SYSTEM.md specifications

import os
import shutil
import sys

class ViewportDetector:
    """
    Detects terminal dimensions and manages display grid layout.
    Aligns with uGRID 16×16 pixel cell system.
    """

    def __init__(self):
        self.width = 80  # Default fallback
        self.height = 24  # Default fallback
        self.grid_width = 0
        self.grid_height = 0
        self.device_type = 'TERMINAL'
        self.ucell_size = 16  # 16×16 pixel cells

    def detect_terminal_size(self):
        """
        Detect current terminal dimensions.

        Returns:
            tuple: (width, height) in characters
        """
        try:
            # Try shutil first (most reliable)
            size = shutil.get_terminal_size()
            self.width = size.columns
            self.height = size.lines
        except (AttributeError, ValueError):
            # Fallback to environment variables
            try:
                self.width = int(os.environ.get('COLUMNS', 80))
                self.height = int(os.environ.get('LINES', 24))
            except (ValueError, TypeError):
                # Use defaults
                self.width = 80
                self.height = 24

        # Calculate grid dimensions (char-based approximation)
        # Each uCELL is ~4 chars wide, ~2 chars tall in text mode
        self.grid_width = self.width // 4
        self.grid_height = self.height // 2

        return (self.width, self.height)

    def classify_device(self):
        """
        Classify device type based on terminal size.
        Per DISPLAY-SYSTEM.md specifications.

        Returns:
            str: Device classification
        """
        if self.width <= 20:
            self.device_type = 'WEARABLE'  # 16×16 grid
        elif self.width <= 50:
            self.device_type = 'MOBILE'     # 40×16 grid
        elif self.width <= 100:
            self.device_type = 'TERMINAL'   # 80×30 grid
        else:
            self.device_type = 'DASHBOARD'  # 120×48 grid

        return self.device_type

    def get_grid_specs(self):
        """
        Get recommended grid specifications for current viewport.

        Returns:
            dict: Grid configuration
        """
        specs = {
            'device_type': self.device_type,
            'terminal_width': self.width,
            'terminal_height': self.height,
            'grid_width': self.grid_width,
            'grid_height': self.grid_height,
            'total_cells': self.grid_width * self.grid_height,
            'ucell_size': self.ucell_size
        }

        # Device-specific recommendations
        if self.device_type == 'WEARABLE':
            specs['recommended_panels'] = 1
            specs['max_columns'] = 1
        elif self.device_type == 'MOBILE':
            specs['recommended_panels'] = 2
            specs['max_columns'] = 2
        elif self.device_type == 'TERMINAL':
            specs['recommended_panels'] = 3
            specs['max_columns'] = 3
        else:  # DASHBOARD
            specs['recommended_panels'] = 6
            specs['max_columns'] = 4

        return specs

    def draw_viewport_map(self):
        """
        Generate ASCII art representation of viewport.

        Returns:
            str: Visual grid map
        """
        map_str = "┌" + "─" * (self.width - 2) + "┐\n"

        # Top info bar
        info = f"uDOS Viewport: {self.width}×{self.height} ({self.device_type})"
        padding = (self.width - len(info) - 2) // 2
        map_str += "│" + " " * padding + info + " " * (self.width - len(info) - padding - 2) + "│\n"

        # Grid representation
        map_str += "├" + "─" * (self.width - 2) + "┤\n"

        # Draw grid cells (simplified)
        cell_width = 4
        cells_per_row = self.width // cell_width

        for row in range(min(self.grid_height, 10)):  # Max 10 rows for display
            line = "│"
            for col in range(cells_per_row):
                if col < self.grid_width:
                    line += "░░░░"
                else:
                    line += "    "
            line += " " * (self.width - len(line) - 1) + "│"
            map_str += line + "\n"

        if self.grid_height > 10:
            map_str += "│" + " " * (self.width // 2 - 5) + "... more ..." + " " * (self.width // 2 - 5) + "│\n"

        # Bottom info
        map_str += "├" + "─" * (self.width - 2) + "┤\n"
        grid_info = f"Grid: {self.grid_width}×{self.grid_height} cells ({self.grid_width * self.grid_height} total)"
        padding = (self.width - len(grid_info) - 2) // 2
        map_str += "│" + " " * padding + grid_info + " " * (self.width - len(grid_info) - padding - 2) + "│\n"
        map_str += "└" + "─" * (self.width - 2) + "┘"

        return map_str

    def get_status_summary(self):
        """
        Get viewport status for session logging.

        Returns:
            dict: Viewport metadata
        """
        return {
            'terminal_size': f"{self.width}×{self.height}",
            'device_type': self.device_type,
            'grid_dimensions': f"{self.grid_width}×{self.grid_height}",
            'total_cells': self.grid_width * self.grid_height,
            'supports_color': sys.stdout.isatty(),
            'ucell_standard': f"{self.ucell_size}×{self.ucell_size}px"
        }
