"""
uDOS Display & Layout Handler (v1.1.5.1)

Manages adaptive UI, screen formatting, progress indicators, and help system.

Extracted from SystemCommandHandler as part of v1.1.5.1 refactoring.

Commands:
- BLANK/CLEAR: Screen clearing with multiple options
- LAYOUT: Adaptive layout management for responsive terminal
- SPLASH: ASCII art splash screens
- HELP: Enhanced help system with search and stats
- PROGRESS: Progress indicator testing and management
"""

from .base_handler import BaseCommandHandler


class DisplayHandler(BaseCommandHandler):
    """Handles display, layout, UI management, and help system."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._layout_manager = None
        self._screen_manager = None
        self._help_manager = None
        self._progress_manager = None

    @property
    def layout_manager(self):
        """Lazy load layout manager."""
        if self._layout_manager is None:
            from core.output.layout_manager import layout_manager
            self._layout_manager = layout_manager
        return self._layout_manager

    @property
    def screen_manager(self):
        """Lazy load screen manager."""
        if self._screen_manager is None:
            from core.output.screen_manager import ScreenManager
            self._screen_manager = ScreenManager()
        return self._screen_manager

    @property
    def help_manager(self):
        """Lazy load help manager."""
        if self._help_manager is None:
            from core.services.help_manager import HelpManager
            self._help_manager = HelpManager()
        return self._help_manager

    @property
    def progress_manager(self):
        """Lazy load progress manager."""
        if self._progress_manager is None:
            from core.utils.progress_manager import progress_manager
            self._progress_manager = progress_manager
        return self._progress_manager

    def handle(self, command, params, grid, parser):
        """Route display and layout commands."""
        handlers = {
            'BLANK': self.handle_blank,
            'CLEAR': self.handle_blank,  # Alias for BLANK
            'LAYOUT': self.handle_layout,
            'SPLASH': self.handle_splash,
            'HELP': self.handle_help,
            'PROGRESS': self.handle_progress
        }

        handler = handlers.get(command)
        if handler:
            return handler(params, grid, parser)

        return False

    def handle_blank(self, params, grid, parser):
        """
        Enhanced screen clearing with multiple options.

        Supports:
        - CLEAR / BLANK: Smart clear (preserve status)
        - CLEAR ALL: Full screen clear
        - CLEAR BUFFER: Clear scrollback buffer
        - CLEAR LAST <n>: Clear last N lines
        - CLEAR GRID: Clear grid display
        - CLEAR LOGS: Clear session logs (requires confirmation)
        - CLEAR HISTORY: Clear command history (requires confirmation)

        Args:
            params: List with optional subcommand
            grid: Grid instance
            parser: Parser instance

        Returns:
            Status message
        """
        # Show help if requested
        if params and params[0].upper() == 'HELP':
            return self.screen_manager.format_clear_help()

        # No params or just CLEAR: Smart clear
        if not params:
            return self.screen_manager.clear_smart()

        # Handle subcommands
        subcommand = params[0].upper()

        if subcommand == 'ALL':
            # CLEAR ALL: Full clear
            return self.screen_manager.clear_full()

        elif subcommand == 'BUFFER':
            # CLEAR BUFFER: Clear scrollback
            return self.screen_manager.clear_buffer()

        elif subcommand == 'LAST':
            # CLEAR LAST <n>: Clear last N lines
            if len(params) < 2:
                return "⚠️  Usage: CLEAR LAST <number>"

            try:
                n = int(params[1])
                return self.screen_manager.clear_last_n_lines(n)
            except ValueError:
                return f"❌ Invalid number: {params[1]}"

        elif subcommand in ['GRID', 'LOGS', 'HISTORY']:
            # Component-specific clearing
            return self.screen_manager.clear_component(subcommand)

        else:
            # Unknown subcommand - show help
            return (f"⚠️  Unknown CLEAR option: {subcommand}\n\n" +
                   self.screen_manager.format_clear_help())

    def handle_help(self, params, grid, parser):
        """
        Display help information with enhanced features.

        Supports:
        - HELP: List all commands by category
        - HELP <command>: Detailed help for specific command
        - HELP SEARCH <query>: Search help content
        - HELP CATEGORY <category>: Filter by category
        - HELP RECENT: Show recently used commands (if usage tracker available)
        - HELP STATS: Show most used commands
        - HELP SESSION: Show current session statistics

        Args:
            params: List with optional command/subcommand
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Formatted help text
        """
        # Handle subcommands
        if params and len(params) >= 1:
            subcommand = params[0].upper()

            # HELP SEARCH <query> (requires query parameter)
            if subcommand == 'SEARCH':
                if len(params) < 2:
                    return "❌ Usage: HELP SEARCH <query>\n💡 Example: HELP SEARCH knowledge"
                query = ' '.join(params[1:])
                return self.help_manager.format_search_results(query)

            # HELP CATEGORY <category> (requires category parameter)
            elif subcommand == 'CATEGORY':
                if len(params) < 2:
                    return "❌ Usage: HELP CATEGORY <category>\n💡 Example: HELP CATEGORY file"
                category = ' '.join(params[1:])
                return self.help_manager.format_help_category(category)

            # HELP RECENT (show recently used commands from usage tracker)
            elif subcommand == 'RECENT':
                if self.usage_tracker:
                    return self.usage_tracker.format_recent_commands(limit=15)
                else:
                    return "❌ Usage tracking not available"

            # HELP STATS (show most used commands)
            elif subcommand == 'STATS':
                if self.usage_tracker:
                    return self.usage_tracker.format_most_used(limit=15)
                else:
                    return "❌ Usage tracking not available"

            # HELP SESSION (show current session statistics)
            elif subcommand == 'SESSION':
                if self.usage_tracker:
                    return self.usage_tracker.format_session_stats()
                else:
                    return "❌ Usage tracking not available"

        # HELP ALL or no params: Show all commands by category
        if not params or params[0].upper() == 'ALL':
            help_text = "╔" + "═"*78 + "╗\n"
            help_text += "║" + " "*26 + "📚 uDOS COMMAND REFERENCE" + " "*27 + "║\n"
            help_text += "╠" + "═"*78 + "╣\n"

            # Display commands by category
            for category, commands in self.help_manager.categories.items():
                if not commands:
                    continue

                help_text += "║ " + category.ljust(77) + "║\n"
                help_text += "║ " + "─"*77 + "║\n"

                for cmd_name in sorted(commands):
                    cmd_data = self.help_manager.get_command_details(cmd_name)
                    if cmd_data:
                        desc = cmd_data.get('DESCRIPTION', '')[:56]
                        help_text += f"║  {cmd_name:<18} - {desc.ljust(56)}║\n"

                help_text += "║" + " "*78 + "║\n"

            # Footer with enhanced hints
            help_text += "╠" + "═"*78 + "╣\n"
            help_text += "║  💡 HELP <command>           - Detailed help for a command".ljust(79) + "║\n"
            help_text += "║  🔍 HELP SEARCH <query>      - Search commands".ljust(79) + "║\n"
            help_text += "║  📁 HELP CATEGORY <name>     - Filter by category".ljust(79) + "║\n"
            help_text += "║  🕐 HELP RECENT              - Show recently used commands".ljust(79) + "║\n"
            help_text += "║  📈 HELP STATS               - Show most used commands".ljust(79) + "║\n"
            help_text += "║  🎯 HELP SESSION             - Show current session statistics".ljust(79) + "║\n"
            help_text += "║  📖 Full docs: https://github.com/fredporter/uDOS/wiki".ljust(79) + "║\n"
            help_text += "╚" + "═"*78 + "╝\n"

            return help_text

        # HELP <command>: Show detailed help for specific command
        else:
            cmd_name = params[0].upper()
            return self.help_manager.format_help_detailed(cmd_name)

    def handle_layout(self, params, grid, parser):
        """
        Adaptive layout management commands for responsive terminal interface.

        Subcommands:
        - LAYOUT INFO                     # Show current layout information
        - LAYOUT MODE <mode>              # Set layout mode (compact/standard/expanded/split/dashboard)
        - LAYOUT RESIZE                   # Force resize detection
        - LAYOUT AUTO ON|OFF              # Toggle automatic resize detection
        - LAYOUT CONFIG <setting> <value> # Update layout configuration
        - LAYOUT TEST                     # Test adaptive formatting
        - LAYOUT DEMO                     # Demo different layout modes
        - LAYOUT SPLIT <content1> <content2> # Create split layout demo

        Args:
            params: List of command parameters
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Formatted layout information or demo results
        """
        # Initialize layout manager
        try:
            from core.output.layout_manager import LayoutMode, ContentType
        except Exception as e:
            return f"❌ Error accessing layout system: {e}"

        if not params:
            # Default: show layout info
            return self._show_layout_info(self.layout_manager)

        subcommand = params[0].upper()

        if subcommand == "INFO":
            return self._show_layout_info(self.layout_manager)

        elif subcommand == "MODE":
            if len(params) < 2:
                return "❌ Usage: LAYOUT MODE <compact|standard|expanded|split|dashboard>"
            mode_name = params[1].upper()
            return self._set_layout_mode(self.layout_manager, mode_name)

        elif subcommand == "RESIZE":
            return self._force_resize_detection(self.layout_manager)

        elif subcommand == "AUTO":
            if len(params) < 2:
                return "❌ Usage: LAYOUT AUTO ON|OFF"
            enable = params[1].upper() == "ON"
            return self._toggle_auto_resize(self.layout_manager, enable)

        elif subcommand == "CONFIG":
            if len(params) < 3:
                return "❌ Usage: LAYOUT CONFIG <setting> <value>"
            setting = params[1].lower()
            value = params[2]
            return self._update_layout_config(self.layout_manager, setting, value)

        elif subcommand == "TEST":
            return self._test_adaptive_formatting(self.layout_manager)

        elif subcommand == "DEMO":
            return self._layout_demo(self.layout_manager)

        elif subcommand == "SPLIT":
            content1 = params[1] if len(params) > 1 else "Sample content 1"
            content2 = params[2] if len(params) > 2 else "Sample content 2"
            return self._demo_split_layout(self.layout_manager, content1, content2)

        else:
            return f"❌ Unknown layout subcommand: {subcommand}\n💡 Use: HELP LAYOUT for usage information"

    def _show_layout_info(self, layout_manager):
        """Show current layout information."""
        try:
            info = layout_manager.get_layout_info()
            dims = info['dimensions']
            config = info['config']

            # Use layout manager to format this response
            content = f"""Terminal Dimensions: {dims['width']}x{dims['height']}
Screen Type: {'📱 Mobile' if dims['is_mobile'] else '🖥️ Wide' if dims['is_wide'] else '💻 Standard'}
Layout Mode: {info['layout_mode'].title()}
Aspect Ratio: {dims['aspect_ratio']:.2f}

Configuration:
• Auto-adapt: {'✅' if config['auto_adapt'] else '❌'}
• Responsive Tables: {'✅' if config['responsive_tables'] else '❌'}
• Adaptive Columns: {'✅' if config['adaptive_columns'] else '❌'}
• Compact Mode: {'✅' if config['compact_mode'] else '❌'}
• Auto-resize: {'✅' if info['auto_resize_enabled'] else '❌'}

Screen Features:
• Wide Screen: {'✅' if dims['is_wide'] else '❌'} (>120 cols)
• Tall Screen: {'✅' if dims['is_tall'] else '❌'} (>30 rows)
• Ultra-wide: {'✅' if dims['is_ultra_wide'] else '❌'} (>200 cols)"""

            from core.output.layout_manager import ContentType
            return layout_manager.format_content(
                content,
                ContentType.STATUS,
                "Layout Manager Status"
            )

        except Exception as e:
            return f"❌ Error showing layout info: {e}"

    def _set_layout_mode(self, layout_manager, mode_name):
        """Set layout mode."""
        try:
            from core.output.layout_manager import LayoutMode

            mode_mapping = {
                'COMPACT': LayoutMode.COMPACT,
                'STANDARD': LayoutMode.STANDARD,
                'EXPANDED': LayoutMode.EXPANDED,
                'SPLIT': LayoutMode.SPLIT,
                'DASHBOARD': LayoutMode.DASHBOARD
            }

            if mode_name not in mode_mapping:
                available = ", ".join(mode_mapping.keys())
                return f"❌ Invalid layout mode: {mode_name}\n💡 Available modes: {available}"

            layout_manager.set_layout_mode(mode_mapping[mode_name])
            return f"🎨 Layout mode set to: {mode_name.lower()}\n✨ Interface will adapt to new layout"

        except Exception as e:
            return f"❌ Error setting layout mode: {e}"

    def _force_resize_detection(self, layout_manager):
        """Force resize detection."""
        try:
            old_dims = layout_manager.current_dimensions
            new_dims = layout_manager._get_terminal_dimensions()

            if (old_dims.width != new_dims.width or old_dims.height != new_dims.height):
                layout_manager._handle_resize(new_dims)
                return (f"🔄 Resize detected and applied!\n"
                       f"📏 Changed from {old_dims.width}x{old_dims.height} to {new_dims.width}x{new_dims.height}\n"
                       f"🎨 Layout mode: {layout_manager.current_mode.value}")
            else:
                return (f"📏 No resize detected\n"
                       f"📊 Current dimensions: {new_dims.width}x{new_dims.height}\n"
                       f"🎨 Layout mode: {layout_manager.current_mode.value}")

        except Exception as e:
            return f"❌ Error detecting resize: {e}"

    def _toggle_auto_resize(self, layout_manager, enable):
        """Toggle automatic resize detection."""
        try:
            layout_manager.auto_resize_enabled = enable

            if enable:
                if not layout_manager._resize_thread or not layout_manager._resize_thread.is_alive():
                    layout_manager._start_resize_monitoring()
                return "🔄 Auto-resize detection enabled\n📐 Terminal layout will automatically adapt to size changes"
            else:
                return "⏸️ Auto-resize detection disabled\n💡 Use 'LAYOUT RESIZE' to manually check for changes"

        except Exception as e:
            return f"❌ Error toggling auto-resize: {e}"

    def _update_layout_config(self, layout_manager, setting, value):
        """Update layout configuration."""
        try:
            # Convert value to appropriate type
            if value.lower() in ['true', 'on', 'yes', '1']:
                value = True
            elif value.lower() in ['false', 'off', 'no', '0']:
                value = False
            elif value.isdigit():
                value = int(value)

            # Map setting names
            setting_map = {
                'auto_adapt': 'auto_adapt',
                'responsive_tables': 'responsive_tables',
                'adaptive_columns': 'adaptive_columns',
                'compact_mode': 'compact_mode',
                'show_borders': 'show_borders',
                'use_unicode': 'use_unicode',
                'content_margin': 'content_margin',
                'min_width': 'min_width',
                'max_width': 'max_width'
            }

            if setting not in setting_map:
                available = ", ".join(setting_map.keys())
                return f"❌ Unknown setting: {setting}\n💡 Available settings: {available}"

            layout_manager.update_config(**{setting_map[setting]: value})
            return f"⚙️ Layout setting updated: {setting} = {value}\n✨ Changes will apply to new content"

        except Exception as e:
            return f"❌ Error updating config: {e}"

    def _test_adaptive_formatting(self, layout_manager):
        """Test adaptive formatting with sample content."""
        try:
            from core.output.layout_manager import ContentType

            # Test different content types
            test_results = []

            # Test table formatting
            table_content = """Name|Type|Size|Date
file1.py|Python|1.2KB|2024-01-15
file2.txt|Text|856B|2024-01-14
document.md|Markdown|3.4KB|2024-01-13"""

            table_result = layout_manager.format_content(table_content, ContentType.TABLE, "File List")
            test_results.append(("📊 Table Format Test", table_result))

            # Test list formatting
            list_content = """• Command history with SQLite persistence
• Advanced tab completion with fuzzy matching
• Dynamic color themes and accessibility features
• Real-time progress indicators for operations
• Session management with workspace persistence"""

            list_result = layout_manager.format_content(list_content, ContentType.LIST, "Feature List")
            test_results.append(("📋 List Format Test", list_result))

            # Test status formatting
            status_content = """System Status: Online
CPU Usage: 23%
Memory: 4.2GB / 8GB
Active Sessions: 3
Auto-save: Enabled"""

            status_result = layout_manager.format_content(status_content, ContentType.STATUS, "System Status")
            test_results.append(("📊 Status Format Test", status_result))

            # Combine results
            final_result = []
            for title, content in test_results:
                final_result.append(f"\n{title}")
                final_result.append("─" * 50)
                final_result.append(content)

            return "\n".join(final_result)

        except Exception as e:
            return f"❌ Error testing adaptive formatting: {e}"

    def _layout_demo(self, layout_manager):
        """Demo different layout capabilities."""
        try:
            from core.output.layout_manager import ContentType

            result = ["🎨 Layout Demo - Adaptive Formatting Examples\n"]
            result.append("=" * 60)

            # Demo 1: Table with different widths
            result.append("\n📊 Demo 1: Responsive Table")
            result.append("─" * 60)
            table_data = "ID|Name|Status|Progress\n1|Task Alpha|Running|75%\n2|Task Beta|Pending|0%\n3|Task Gamma|Complete|100%"
            result.append(layout_manager.format_content(table_data, ContentType.TABLE))

            # Demo 2: List formatting
            result.append("\n📋 Demo 2: Formatted List")
            result.append("─" * 60)
            list_data = "• First item in list\n• Second item with more detail\n• Third item is quite long and should wrap nicely"
            result.append(layout_manager.format_content(list_data, ContentType.LIST))

            # Demo 3: Current layout info
            result.append("\n📐 Demo 3: Current Layout Settings")
            result.append("─" * 60)
            info = layout_manager.get_layout_info()
            result.append(f"Mode: {info['layout_mode']}")
            result.append(f"Dimensions: {info['dimensions']['width']}x{info['dimensions']['height']}")
            result.append(f"Screen Type: {info['screen_type']}")

            return "\n".join(result)

        except Exception as e:
            return f"❌ Error in layout demo: {e}"

    def _demo_split_layout(self, layout_manager, content1, content2):
        """Demo split layout with two content areas."""
        try:
            from core.output.layout_manager import ContentType

            # Format both content areas
            left = layout_manager.format_content(content1, ContentType.TEXT, "Left Panel")
            right = layout_manager.format_content(content2, ContentType.TEXT, "Right Panel")

            # Simple side-by-side display (terminal width allowing)
            info = layout_manager.get_layout_info()
            width = info['dimensions']['width']

            if width < 80:
                # Stack vertically on narrow screens
                return f"{left}\n{'─'*width}\n{right}"
            else:
                # Side by side on wide screens
                half = width // 2
                result = ["Split Layout Demo (Side-by-Side)", "=" * width]

                left_lines = left.split('\n')
                right_lines = right.split('\n')
                max_lines = max(len(left_lines), len(right_lines))

                for i in range(max_lines):
                    l = left_lines[i] if i < len(left_lines) else ""
                    r = right_lines[i] if i < len(right_lines) else ""
                    result.append(f"{l:<{half}} │ {r}")

                return "\n".join(result)

        except Exception as e:
            return f"❌ Error in split layout demo: {e}"

    def handle_splash(self, params, grid, parser):
        """
        Display ASCII art splash screen.

        Modes:
        - SPLASH or SPLASH LOGO: Display uDOS logo
        - SPLASH <text>: Display custom text as ASCII art
        - SPLASH FILE <path>: Load ASCII art from file
        """
        # Import splash module
        from core.output.splash import print_splash_screen

        if not params or (params and params[0].upper() == 'LOGO'):
            # Default: show uDOS logo
            print_splash_screen()
            return ""  # Splash already printed

        elif params[0].upper() == 'FILE' and len(params) > 1:
            # Load from file
            from pathlib import Path
            filepath = Path(params[1])

            if not filepath.exists():
                return f"❌ File not found: {filepath}"

            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                print(content)
                return ""
            except Exception as e:
                return f"❌ Error reading file: {e}"

        else:
            # Custom text - display in a box
            text = ' '.join(params)
            width = max(len(text) + 4, 40)

            print("╔" + "═" * (width - 2) + "╗")
            padding = (width - len(text) - 2) // 2
            print("║" + " " * padding + text + " " * (width - len(text) - padding - 2) + "║")
            print("╚" + "═" * (width - 2) + "╝")
            return ""

    def handle_progress(self, params, grid, parser):
        """
        Progress indicator testing and management commands.

        Subcommands:
        - PROGRESS TEST               # Test basic progress indicator
        - PROGRESS TEST MULTI         # Test multi-stage progress
        - PROGRESS TEST SEARCH        # Test file search with progress
        - PROGRESS LIST               # List active progress indicators
        - PROGRESS CANCEL [id]        # Cancel active progress (or all)
        - PROGRESS DEMO               # Full demo of all progress types

        Args:
            params: List of command parameters
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Formatted progress information or demo results
        """
        if not params:
            # Default: show active progress indicators
            return self._show_active_progress()

        subcommand = params[0].upper()

        if subcommand == "TEST":
            if len(params) > 1 and params[1].upper() == "MULTI":
                return self._test_multi_stage_progress()
            elif len(params) > 1 and params[1].upper() == "SEARCH":
                return self._test_search_progress()
            else:
                return self._test_basic_progress()

        elif subcommand == "LIST":
            return self._list_active_progress()

        elif subcommand == "CANCEL":
            progress_id = params[1] if len(params) > 1 else None
            return self._cancel_progress(progress_id)

        elif subcommand == "DEMO":
            return self._run_progress_demo()

        else:
            return f"❌ Unknown progress subcommand: {subcommand}\n💡 Use: HELP PROGRESS for usage information"

    def _show_active_progress(self):
        """Show current active progress indicators."""
        try:
            active_count = self.progress_manager.get_active_count()
            if active_count == 0:
                return "📊 No active progress indicators\n💡 Use: PROGRESS TEST to test progress features"

            result = [f"📊 Active Progress Indicators ({active_count})"]
            result.append("=" * 50)

            for task_id, indicator in self.progress_manager.indicators.items():
                if indicator.status == "running":
                    elapsed = indicator.last_update - indicator.start_time
                    result.append(f"• {task_id}: {indicator.description}")
                    result.append(f"  Status: {indicator.status} | Elapsed: {elapsed}")
                    if indicator.total:
                        percentage = (indicator.current / indicator.total * 100) if indicator.total > 0 else 0
                        result.append(f"  Progress: {indicator.current}/{indicator.total} ({percentage:.1f}%)")

            result.append("\n💡 Use: PROGRESS CANCEL to stop all progress")
            return "\n".join(result)

        except Exception as e:
            return f"❌ Error checking progress: {e}"

    def _test_basic_progress(self):
        """Test basic progress indicator."""
        import threading
        import time

        try:
            from core.utils.progress_manager import ProgressConfig

            # Create a simple progress test
            config = ProgressConfig(show_time_estimate=True, show_percentage=True)
            progress = self.progress_manager.create_progress(
                "test_basic",
                "Testing basic progress indicator",
                100,
                config
            )

            def test_work():
                progress.start()
                for i in range(101):
                    time.sleep(0.05)  # Simulate work
                    progress.update(i, f"Processing item {i}")
                    if progress.cancelled:
                        break
                progress.complete("Basic test completed!")

                # Clean up after a delay
                time.sleep(3)
                self.progress_manager.remove_progress("test_basic")

            # Start test in background
            threading.Thread(target=test_work, daemon=True).start()

            return "🚀 Started basic progress test (100 items, 5 seconds)\n👀 Watch the progress indicator above\n💡 Use Ctrl+C to cancel"

        except Exception as e:
            return f"❌ Error starting progress test: {e}"

    def _test_multi_stage_progress(self):
        """Test multi-stage progress indicator."""
        import threading
        import time

        try:
            from core.utils.progress_manager import ProgressConfig

            stages = ["Initialization", "Data Processing", "Analysis", "Finalization"]
            config = ProgressConfig(show_time_estimate=True, width=30)

            multi_progress = self.progress_manager.create_multi_stage_progress(
                "test_multi",
                stages,
                config
            )

            def test_multi_work():
                for stage_idx, stage_name in enumerate(stages):
                    items_in_stage = 50 + (stage_idx * 10)  # Variable stage lengths
                    multi_progress.start_stage(stage_idx, stage_name, items_in_stage)

                    for i in range(items_in_stage + 1):
                        time.sleep(0.02)  # Simulate work
                        multi_progress.update_stage(i, f"{stage_name}: item {i}")

                        # Check for cancellation
                        if multi_progress.current_indicator and multi_progress.current_indicator.cancelled:
                            return

                    multi_progress.complete_stage(f"{stage_name} completed")
                    time.sleep(0.5)  # Brief pause between stages

                multi_progress.complete("All stages completed successfully!")

                # Clean up after delay
                time.sleep(3)
                self.progress_manager.remove_progress("test_multi")

            # Start test in background
            threading.Thread(target=test_multi_work, daemon=True).start()

            return f"🚀 Started multi-stage progress test ({len(stages)} stages)\n👀 Watch the progress indicators above\n💡 Use Ctrl+C to cancel"

        except Exception as e:
            return f"❌ Error starting multi-stage test: {e}"

    def _test_search_progress(self):
        """Test search operation with progress."""
        try:
            return "💡 Search progress demo requires FileHandler integration"
        except Exception as e:
            return f"❌ Error testing search progress: {e}"

    def _list_active_progress(self):
        """List all active progress indicators with details."""
        try:
            active_indicators = []

            # Check regular indicators
            for task_id, indicator in self.progress_manager.indicators.items():
                if indicator.status == "running":
                    active_indicators.append({
                        'id': task_id,
                        'type': 'simple',
                        'description': indicator.description,
                        'progress': f"{indicator.current}/{indicator.total}" if indicator.total else "N/A",
                        'elapsed': str(indicator.last_update - indicator.start_time).split('.')[0]
                    })

            # Check multi-stage indicators
            for task_id, indicator in self.progress_manager.multi_stage_indicators.items():
                if indicator.status == "running":
                    overall_progress = indicator.get_overall_progress()
                    active_indicators.append({
                        'id': task_id,
                        'type': 'multi-stage',
                        'description': f"Stage {indicator.current_stage + 1}/{len(indicator.stages)}",
                        'progress': f"{overall_progress:.1f}%",
                        'elapsed': str(indicator.start_time).split('.')[0]
                    })

            if not active_indicators:
                return "📊 No active progress indicators\n💡 Use: PROGRESS TEST to start a test"

            result = ["📊 Active Progress Indicators"]
            result.append("=" * 80)
            result.append(f"{'ID':<15} {'Type':<12} {'Description':<30} {'Progress':<15} {'Elapsed':<10}")
            result.append("-" * 80)

            for indicator in active_indicators:
                result.append(
                    f"{indicator['id']:<15} {indicator['type']:<12} "
                    f"{indicator['description']:<30} {indicator['progress']:<15} {indicator['elapsed']:<10}"
                )

            result.append(f"\n💡 Use: PROGRESS CANCEL <id> to cancel specific progress")
            return "\n".join(result)

        except Exception as e:
            return f"❌ Error listing progress: {e}"

    def _cancel_progress(self, progress_id):
        """Cancel progress indicator(s)."""
        try:
            if progress_id:
                # Cancel specific progress
                if progress_id in self.progress_manager.indicators:
                    self.progress_manager.indicators[progress_id].cancel("Cancelled by user")
                    self.progress_manager.remove_progress(progress_id)
                    return f"🚫 Cancelled progress: {progress_id}"
                elif progress_id in self.progress_manager.multi_stage_indicators:
                    indicator = self.progress_manager.multi_stage_indicators[progress_id]
                    if indicator.current_indicator:
                        indicator.current_indicator.cancel("Cancelled by user")
                    self.progress_manager.remove_progress(progress_id)
                    return f"🚫 Cancelled multi-stage progress: {progress_id}"
                else:
                    return f"❌ Progress indicator not found: {progress_id}"
            else:
                # Cancel all progress
                self.progress_manager.cancel_all()
                return "🚫 Cancelled all active progress indicators"

        except Exception as e:
            return f"❌ Error cancelling progress: {e}"

    def _run_progress_demo(self):
        """Run a comprehensive demo of all progress features."""
        import threading
        import time

        try:
            from core.utils.progress_manager import ProgressConfig

            def demo_sequence():
                # Demo 1: Basic determinate progress
                config1 = ProgressConfig(style="block", show_time_estimate=True)
                p1 = self.progress_manager.create_progress("demo_basic", "Demo: Basic Progress", 50, config1)
                p1.start()

                for i in range(51):
                    time.sleep(0.1)
                    p1.update(i, f"Processing item {i}/50")
                p1.complete("Basic demo completed")
                time.sleep(1)

                # Demo 2: Indeterminate progress
                config2 = ProgressConfig(show_cancel_hint=True)
                p2 = self.progress_manager.create_progress("demo_spinner", "Demo: Indeterminate Progress")
                p2.start()

                time.sleep(3)  # Spinner for 3 seconds
                p2.complete("Indeterminate demo completed")
                time.sleep(1)

                # Demo 3: Multi-stage progress
                stages = ["Setup", "Processing", "Cleanup"]
                config3 = ProgressConfig(style="bar", width=25)
                p3 = self.progress_manager.create_multi_stage_progress("demo_multi", stages, config3)

                for i, stage in enumerate(stages):
                    p3.start_stage(i, f"Demo: {stage}", 20)
                    for j in range(21):
                        time.sleep(0.05)
                        p3.update_stage(j, f"{stage} item {j}")
                    p3.complete_stage(f"{stage} completed")

                p3.complete("Multi-stage demo completed")

                # Cleanup
                time.sleep(2)
                self.progress_manager.cleanup_completed()

            # Start demo in background
            threading.Thread(target=demo_sequence, daemon=True).start()

            return ("🎭 Starting comprehensive progress demo!\n"
                   "👀 Watch for 3 different types of progress indicators:\n"
                   "   1. Basic determinate progress (50 items)\n"
                   "   2. Indeterminate spinner (3 seconds)\n"
                   "   3. Multi-stage progress (3 stages)\n"
                   "⏱️ Total demo time: ~15 seconds")

        except Exception as e:
            return f"❌ Error starting progress demo: {e}"
