def print_splash_screen():
    """
    Prints the uDOS splash screen with rainbow gradient colors.
    """
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        from rich import box

        console = Console(force_terminal=True, force_interactive=False)

        # Rainbow gradient ASCII art (each line different color)
        splash_lines = [
            "██╗   ██╗██████╗  ██████╗ ███████╗",
            "██║   ██║██╔══██╗██╔═══██╗██╔════╝",
            "██║   ██║██║  ██║██║   ██║███████╗",
            "██║   ██║██║  ██║██║   ██║╚════██║",
            "╚██████╔╝██████╔╝╚██████╔╝███████║",
            " ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝"
        ]

        # Rainbow gradient colors (vivid palette)
        colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]

        # Build colored splash
        splash_text = Text()
        for i, line in enumerate(splash_lines):
            splash_text.append(line + "\n", style=f"bold {colors[i % len(colors)]}")

        # Subtitle with gradient
        subtitle = Text()
        subtitle.append("uDOS ", style="bold cyan")
        subtitle.append("v1.2.8", style="bold yellow")
        subtitle.append(" - ", style="white")
        subtitle.append("Offline-First Survival OS", style="bold green")

        # Commands help
        help_text = Text()
        help_text.append("💡 Type ", style="dim")
        help_text.append("HELP", style="bold cyan")
        help_text.append(" for commands | ", style="dim")
        help_text.append("CONFIG LIST", style="bold yellow")
        help_text.append(" for settings", style="dim")

        syntax_text = Text()
        syntax_text.append("📝 Syntax: ", style="dim")
        syntax_text.append("COMMAND(options|$VARIABLE|'string')", style="bold green")
        syntax_text.append(" or ", style="dim")
        syntax_text.append("MODULE COMMAND(params)", style="bold magenta")

        # Create panel with colored border
        panel_content = Text.assemble(
            splash_text,
            "\n",
            subtitle,
            "\n",
            ("─" * 60, "dim"),
            "\n",
            help_text,
            "\n",
            syntax_text
        )

        panel = Panel(
            panel_content,
            border_style="bold cyan",
            box=box.DOUBLE,
            padding=(1, 2)
        )

        console.print(panel)
        print()  # Extra line for spacing
        return  # Success - exit early

    except ImportError:
        # Rich library not installed - use plain text fallback
        pass
    except Exception as e:
        # Rich rendering failed - use plain text fallback
        # Uncomment for debugging: print(f"DEBUG: Rich rendering failed: {e}")
        pass

    # Fallback to plain text
    splash_text = r"""
██╗   ██╗██████╗  ██████╗ ███████╗
██║   ██║██╔══██╗██╔═══██╗██╔════╝
██║   ██║██║  ██║██║   ██║███████╗
██║   ██║██║  ██║██║   ██║╚════██║
╚██████╔╝██████╔╝╚██████╔╝███████║
 ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝
"""
    print(splash_text)
    print("uDOS v1.2.8 - Offline-First Survival OS")
    print("="*50)
    print("Type HELP for commands | CONFIG LIST for settings")
    print("Syntax: COMMAND(options|$VARIABLE|'string') or MODULE COMMAND(params)")
    print()


def print_viewport_measurement(viewport, delay=1.0):
    """
    Display full-screen viewport measurement with colorful block graphics.
    Shows terminal dimensions and grid visualization.

    Args:
        viewport: ViewportDetector instance with terminal size
        delay: Seconds to display before continuing
    """
    import time
    import sys

    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        from rich import box

        console = Console()

        width = viewport.width
        height = viewport.height
        device = viewport.device_type

        # Clear screen for full effect (only if stdout is a terminal)
        if sys.stdout.isatty():
            console.clear()

        # Calculate grid specs
        specs = viewport.get_grid_specs()
        grid_w = specs['grid_width']
        grid_h = specs['grid_height']
        total_cells = specs['total_cells']

        # Create measurement table
        table = Table(
            title="🌀 uDOS VIEWPORT MEASUREMENT",
            title_style="bold cyan",
            border_style="bold blue",
            show_header=False,
            box=box.DOUBLE,
            padding=(0, 2)
        )

        table.add_column("Property", style="bold yellow", no_wrap=True)
        table.add_column("Value", style="bold green")

        table.add_row("📐 Terminal Size", f"{width} × {height} characters")
        table.add_row("🖥️  Device Type", device)
        table.add_row("📊 Grid Dimensions", f"{grid_w} × {grid_h} cells")
        table.add_row("🔢 Total Cells", f"{total_cells:,}")

        console.print(table)

        # Visual boundary representation - compact ASCII dashboard
        console.print()

        # Title bar - aligned to 50 chars total width
        console.print(f"    [bold cyan]┌─ VIEWPORT {'─' * 39}┐[/]")

        # Info row - aligned
        info_text = f"{width}×{height} • {grid_w}×{grid_h} grid • {device}"
        console.print(f"    [bold cyan]│[/] [yellow]{info_text:^46}[/] [bold cyan]│[/]")

        # Separator - aligned
        console.print(f"    [bold cyan]├{'─' * 48}┤[/]")

        # Visual grid - aligned inner box (44 chars)
        colors = ['cyan', 'blue', 'magenta', 'blue', 'cyan']
        for i in range(5):
            color = colors[i]
            if i == 0:
                inner = f"[dim]┌{'─' * 44}┐[/]"
            elif i == 4:
                inner = f"[dim]└{'─' * 44}┘[/]"
            else:
                inner = f"[dim]│{' ' * 44}│[/]"
            console.print(f"    [bold {color}]│[/] {inner} [bold {color}]│[/]")

        # Bottom with status - aligned
        console.print(f"    [bold cyan]└─ Detected {'─' * 39}┘[/]")
        console.print()

        # Delay before continuing
        time.sleep(delay)

    except ImportError:
        # Fallback to plain text if rich not available
        width = viewport.width
        height = viewport.height
        device = viewport.device_type

        # Clear screen for full effect (only if stdout is a terminal)
        if sys.stdout.isatty():
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
            lines.append("║" + " " * inner_margin + "└" + "─" * (inner_width - 2) + "┘" + " " * (width - inner_width - inner_margin - 2) + "║")

        # Fill remaining vertical space
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
            print(line, flush=True)

        # Delay for visual effect
        time.sleep(delay)

        # Clear screen after measurement (only if stdout is a terminal)
        if sys.stdout.isatty():
            print('\033[2J\033[H', end='', flush=True)

    except (BrokenPipeError, IOError, OSError):
        # Gracefully handle output issues
        pass
    except Exception:
        # For any other unexpected error, fail silently
        pass
