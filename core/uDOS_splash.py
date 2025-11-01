def print_splash_screen():
    """
    Prints the uDOS splash screen.
    """
    splash_text = r"""
██╗   ██╗██████╗  ██████╗ ███████╗
██║   ██║██╔══██╗██╔═══██╗██╔════╝
██║   ██║██║  ██║██║   ██║███████╗
██║   ██║██║  ██║██║   ██║╚════██║
╚██████╔╝██████╔╝╚██████╔╝███████║
 ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝
"""
    print(splash_text)
    print("uDOS v1.0.0 - Smart Commands & Interactive System")
    print("="*50)


def print_viewport_measurement(viewport, delay=1.0):
    """
    Display full-screen viewport measurement with block graphics.
    Shows terminal dimensions and grid visualization.

    Args:
        viewport: ViewportDetector instance with terminal size
        delay: Seconds to display before continuing
    """
    import time
    import sys

    width = viewport.width
    height = viewport.height
    device = viewport.device_type

    # Clear screen for full effect
    print('\033[2J\033[H', end='', flush=True)

    # Calculate grid specs
    specs = viewport.get_grid_specs()
    grid_w = specs['grid_width']
    grid_h = specs['grid_height']
    total_cells = specs['total_cells']

    # Build the measurement display
    lines = []

    # Top border (full width)
    lines.append("╔" + "═" * (width - 2) + "╗")

    # Title section
    title = "🌀 uDOS VIEWPORT MEASUREMENT"
    padding = (width - len(title) - 2) // 2
    lines.append("║" + " " * padding + title + " " * (width - len(title) - padding - 2) + "║")
    lines.append("╠" + "═" * (width - 2) + "╣")

    # Empty line
    lines.append("║" + " " * (width - 2) + "║")

    # Terminal dimensions
    term_line = f"  📐 Terminal: {width} × {height} characters"
    lines.append("║" + term_line.ljust(width - 2) + "║")

    # Device type
    device_line = f"  🖥️  Device: {device}"
    lines.append("║" + device_line.ljust(width - 2) + "║")

    # Grid info
    grid_line = f"  📊 Grid: {grid_w} × {grid_h} cells ({total_cells} total)"
    lines.append("║" + grid_line.ljust(width - 2) + "║")

    # Empty line
    lines.append("║" + " " * (width - 2) + "║")

    # Divider
    lines.append("╠" + "═" * (width - 2) + "╣")

    # Empty line
    lines.append("║" + " " * (width - 2) + "║")

    # Visual grid representation (show a scaled version)
    # Calculate how much space we have for the grid
    remaining_height = height - len(lines) - 5  # Reserve space for bottom

    if remaining_height > 5:
        # Center text
        center_text = "TERMINAL BOUNDARY VISUALIZATION"
        center_padding = (width - len(center_text) - 2) // 2
        lines.append("║" + " " * center_padding + center_text + " " * (width - len(center_text) - center_padding - 2) + "║")
        lines.append("║" + " " * (width - 2) + "║")

        # Draw visual grid representation
        # Top of inner box
        inner_width = min(width - 8, 60)  # Leave margins
        inner_margin = (width - inner_width - 2) // 2

        lines.append("║" + " " * inner_margin + "┌" + "─" * (inner_width - 2) + "┐" + " " * (width - inner_width - inner_margin - 2) + "║")

        # Fill middle with block pattern
        grid_rows = min(remaining_height - 4, 6)
        for i in range(grid_rows):
            if i == grid_rows // 2:
                # Middle row - show dimensions
                dim_text = f"{width}×{height}"
                text_padding = (inner_width - len(dim_text) - 2) // 2
                inner_content = " " * text_padding + dim_text + " " * (inner_width - len(dim_text) - text_padding - 2)
            else:
                # Show block pattern
                block_count = (inner_width - 2) // 2
                inner_content = ("█░" * block_count)[:inner_width - 2]

            lines.append("║" + " " * inner_margin + "│" + inner_content + "│" + " " * (width - inner_width - inner_margin - 2) + "║")

        # Bottom of inner box
        lines.append("║" + " " * inner_margin + "└" + "─" * (inner_width - 2) + "┘" + " " * (width - inner_width - inner_margin - 2) + "║")    # Fill remaining vertical space
    while len(lines) < height - 3:
        lines.append("║" + " " * (width - 2) + "║")

    # Status line
    status = "⏳ Measuring terminal geometry..."
    status_padding = (width - len(status) - 2) // 2
    lines.append("║" + " " * status_padding + status + " " * (width - len(status) - status_padding - 2) + "║")

    # Bottom border
    lines.append("╚" + "═" * (width - 2) + "╝")

    # Print all lines
    for line in lines:
        # Ensure line doesn't exceed terminal width
        if len(line) > width:
            line = line[:width-3] + "║"
        print(line)

    # Delay for visual effect
    time.sleep(delay)

    # Clear screen after measurement
    print('\033[2J\033[H', end='', flush=True)
