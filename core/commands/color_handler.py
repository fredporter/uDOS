"""
COLOR Command Handler - Showcase colorful TUI elements
Demonstrates all color UI features: splash, syntax highlighting, page breaks, meters, etc.
"""

def handle_color(params):
    """
    COLOR command - Showcase colorful TUI features.

    Syntax:
        COLOR                    # Show all demos
        COLOR splash             # Show rainbow splash
        COLOR syntax             # Show syntax highlighting demo
        COLOR breaks             # Show page break styles
        COLOR meters             # Show progress meters
        COLOR status             # Show status indicators
        COLOR themes             # Show all themes
        COLOR demo               # Interactive demo

    Examples:
        COLOR                    # Full showcase
        COLOR splash             # Just the splash screen
        COLOR demo               # Interactive theme picker
    """
    try:
        from core.output.splash import print_splash_screen
        from core.output.color_ui import ColorUI, get_color_ui
        from core.output.syntax_highlighter import UPYHighlighter, highlight_upy
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        import time

        console = Console()
        ui = get_color_ui()

        # Parse params
        command = params.strip().lower() if params else 'all'

        if command in ['all', 'splash']:
            console.clear()
            print_splash_screen()
            if command == 'splash':
                return "Rainbow splash displayed!"
            time.sleep(1)

        if command in ['all', 'syntax']:
            console.print("\n[bold cyan]═══ Syntax Highlighting Demo ═══[/]\n")

            sample_code = '''# Sample uPY Script
LOAD("water/purification")
SET($LOCATION, "AU-BNE")
SEARCH("fire starting", "fire")
GENERATE("water filter", "survival")

# Variables and functions
$SYSTEM.VERSION
calculate_distance($FROM, $TO)

# Strings and numbers
message = "Hello, uDOS!"
count = 42
ratio = 3.14'''

            highlight_upy(sample_code, line_numbers=True)
            if command == 'syntax':
                return "Syntax highlighting demonstrated!"
            time.sleep(1)

        if command in ['all', 'breaks']:
            console.print("\n[bold cyan]═══ Page Break Styles ═══[/]\n")

            for theme in ['foundation', 'galaxy', 'neon', 'retro']:
                console.print(f"\n[bold]{theme.upper()} Theme:[/]")
                ui.page_break(theme=theme, style='simple')
                ui.page_break(theme=theme, style='double')
                ui.page_break(theme=theme, style='dotted')
                ui.page_break(theme=theme, style='decorative')
                console.print()

            if command == 'breaks':
                return "Page breaks demonstrated!"
            time.sleep(1)

        if command in ['all', 'meters']:
            console.print("\n[bold cyan]═══ Progress Meters Demo ═══[/]\n")

            # Different meter levels
            ui.meter("System Health", 95, theme='foundation')
            ui.meter("Memory Usage", 72, theme='galaxy')
            ui.meter("CPU Load", 45, theme='neon')
            ui.meter("Disk Space", 18, theme='retro')

            console.print()

            # Animated progress bar
            with ui.progress_bar("Processing", total=100, theme='foundation') as progress:
                task = progress.add_task("Loading", total=100)
                for i in range(100):
                    progress.update(task, advance=1)
                    time.sleep(0.02)

            if command == 'meters':
                return "Progress meters demonstrated!"
            time.sleep(1)

        if command in ['all', 'status']:
            console.print("\n[bold cyan]═══ Status Indicators ═══[/]\n")

            ui.status_indicator("Operation completed successfully", "success")
            ui.status_indicator("Connection established", "success")
            ui.status_indicator("Warning: Low memory", "warning")
            ui.status_indicator("API key not configured", "warning")
            ui.status_indicator("Failed to load module", "error")
            ui.status_indicator("Network timeout", "error")
            ui.status_indicator("System initialized", "info")
            ui.status_indicator("Checking for updates", "info")

            if command == 'status':
                return "Status indicators demonstrated!"
            time.sleep(1)

        if command in ['all', 'themes']:
            console.print("\n[bold cyan]═══ Theme Showcase ═══[/]\n")

            themes = ['foundation', 'galaxy', 'neon', 'retro']

            for theme in themes:
                ui.section_divider(f"{theme.upper()} THEME", theme=theme)
                console.print()

                ui.status_indicator(f"{theme} theme - success", "success")
                ui.status_indicator(f"{theme} theme - warning", "warning")
                ui.meter(f"{theme} metric", 75, theme=theme, width=30)

                console.print()

            if command == 'themes':
                return "All themes demonstrated!"
            time.sleep(1)

        if command == 'demo':
            console.clear()

            # Interactive demo
            panel = Panel(
                "[bold cyan]🎨 Color UI Interactive Demo[/]\n\n"
                "This demo showcases all colorful TUI features:\n"
                "• Rainbow gradient splash screen\n"
                "• Syntax highlighting for .upy scripts\n"
                "• Themed page breaks and dividers\n"
                "• Progress meters and animated bars\n"
                "• Status indicators with icons\n"
                "• 4 color themes (foundation/galaxy/neon/retro)",
                title="✨ uDOS Color System",
                border_style="bold magenta",
                padding=(1, 2)
            )
            console.print(panel)

            # Show rainbow text
            console.print()
            ui.rainbow_text("█ RAINBOW GRADIENT TEXT █")
            ui.gradient_text("▓ TWO-COLOR GRADIENT ▓", "cyan", "magenta")

            return "Interactive demo complete!"

        # Unknown command
        if command not in ['all', 'splash', 'syntax', 'breaks', 'meters', 'status', 'themes', 'demo']:
            return f"Unknown COLOR command: {command}\nUse: COLOR [splash|syntax|breaks|meters|status|themes|demo]"

        return "Color showcase complete! ✨"

    except ImportError as e:
        return f"Error: Missing dependency ({e}). Install with: pip install rich>=13.0.0"
    except Exception as e:
        return f"Error in COLOR command: {e}"
