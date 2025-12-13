"""
uDOS v1.0.0 - System Command Handler (Modular)

Handles system administration commands by delegating to specialized handlers:
- REPAIR: Delegates to RepairHandler for comprehensive diagnostics and maintenance
- STATUS, DASHBOARD, VIEWPORT, PALETTE: Delegates to DashboardHandler
- WIZARD (old SETUP): Setup wizard for first-time configuration
- CONFIG: Delegates to ConfigurationHandler for settings management
- REBOOT, DESTROY: Core system commands handled directly
"""

import os
import sys
import json
import shutil
from pathlib import Path
from .base_handler import BaseCommandHandler
from core.utils.filename_generator import FilenameGenerator


class SystemCommandHandler(BaseCommandHandler):
    """Modular system administration handler with specialized delegation."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # v1.2.23: FilenameGenerator for system exports and reports
        config = kwargs.get('config')
        self.filename_gen = FilenameGenerator(config=config)

        # Import services only when needed (lazy loading)
        self._startup_module = None
        self._settings_manager = None
        self._workspace_manager = None
        self._config_manager = None
        self._help_manager = None
        self._screen_manager = None
        self._setup_wizard = None
        self._usage_tracker = None

    @property
    def startup(self):
        """Lazy load startup module."""
        if self._startup_module is None:
            from core import uDOS_startup
            self._startup_module = uDOS_startup
        return self._startup_module

    @property
    def settings_manager(self):
        """Lazy load settings manager."""
        if self._settings_manager is None:
            from core.services.settings_manager import SettingsManager
            self._settings_manager = SettingsManager()
        return self._settings_manager

    @property
    def workspace_manager(self):
        """Lazy load workspace manager."""
        if self._workspace_manager is None:
            from core.services.workspace_manager import WorkspaceManager
            self._workspace_manager = WorkspaceManager()
        return self._workspace_manager

    @property
    def config_manager(self):
        """Lazy load config manager (v1.5.0: Uses new ConfigManager)."""
        if self._config_manager is None:
            from core.uDOS_main import get_config
            self._config_manager = get_config()
        return self._config_manager

    @property
    def help_manager(self):
        """Lazy load help manager."""
        if self._help_manager is None:
            from core.services.help_manager import HelpManager
            self._help_manager = HelpManager()
        return self._help_manager

    @property
    def screen_manager(self):
        """Lazy load screen manager."""
        if self._screen_manager is None:
            from core.output.screen_manager import ScreenManager
            self._screen_manager = ScreenManager()
        return self._screen_manager

    @property
    def setup_wizard(self):
        """Lazy load setup wizard."""
        if self._setup_wizard is None:
            from core.services.setup_wizard import SetupWizard
            self._setup_wizard = SetupWizard()
        return self._setup_wizard

    @property
    def usage_tracker(self):
        """Lazy load usage tracker."""
        if self._usage_tracker is None:
            from core.utils.usage_tracker import UsageTracker
            self._usage_tracker = UsageTracker()
        return self._usage_tracker

    def _get_display_handler(self):
        """Helper to create DisplayHandler with current context."""
        from .display_handler import DisplayHandler
        return DisplayHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

    def _get_dashboard_handler(self):
        """Helper to create DashboardHandler with current context."""
        from .dashboard_handler import DashboardHandler
        return DashboardHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

    def _get_config_handler(self):
        """Helper to create ConfigurationHandler with current context."""
        from .configuration_handler import ConfigurationHandler
        return ConfigurationHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

    def _get_repair_handler(self):
        """Helper to create RepairHandler with current context."""
        from .repair_handler import RepairHandler
        return RepairHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

    def _get_shakedown_handler(self):
        """Helper to create ShakedownHandler with current context."""
        from .shakedown_handler import ShakedownHandler
        return ShakedownHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

    @property
    def dev_mode_manager(self):
        """Lazy load DEV MODE manager (v1.5.0)."""
        if not hasattr(self, '_dev_mode_manager') or self._dev_mode_manager is None:
            from core.services.dev_mode_manager import get_dev_mode_manager
            self._dev_mode_manager = get_dev_mode_manager(config_manager=self.config_manager)
        return self._dev_mode_manager

    @property
    def variable_handler(self):
        """Lazy load variable handler."""
        if not hasattr(self, '_variable_handler') or self._variable_handler is None:
            from .variable_handler import VariableHandler
            self._variable_handler = VariableHandler(**self.__dict__)
        return self._variable_handler

    @property
    def environment_handler(self):
        """Lazy load environment handler."""
        if not hasattr(self, '_environment_handler') or self._environment_handler is None:
            from .environment_handler import EnvironmentHandler
            self._environment_handler = EnvironmentHandler(**self.__dict__)
        return self._environment_handler

    @property
    def environment_handler(self):
        """Lazy load environment handler."""
        if not hasattr(self, '_environment_handler') or self._environment_handler is None:
            from .environment_handler import EnvironmentHandler
            self._environment_handler = EnvironmentHandler(**self.__dict__)
        return self._environment_handler

    @property
    def output_handler(self):
        """Lazy load output handler."""
        if not hasattr(self, '_output_handler') or self._output_handler is None:
            from .output_handler import OutputHandler
            self._output_handler = OutputHandler(**self.__dict__)
        return self._output_handler

    def handle_help(self, params, grid, parser):
        """HELP command - show command reference - uses modern HelpHandler."""
        # Import here to avoid circular dependency
        from .help_handler import HelpHandler
        
        # Create handler and delegate
        help_handler = HelpHandler(viewport=self.viewport, logger=self.logger)
        return help_handler.handle(params)

    def handle_blank(self, params, grid, parser):
        """Clear screen (BLANK) - delegates to DisplayHandler."""
        return self._get_display_handler().handle_blank(params, grid, parser)

    def handle_splash(self, params, grid, parser):
        """Show splash screen - delegates to DisplayHandler."""
        return self._get_display_handler().handle_splash(params, grid, parser)

    def handle_layout(self, params, grid, parser):
        """Screen layout management - delegates to DisplayHandler."""
        return self._get_display_handler().handle_layout(params, grid, parser)

    def handle_progress(self, params, grid, parser):
        """Show progress indicators - delegates to DisplayHandler."""
        return self._get_display_handler().handle_progress(params, grid, parser)

    def handle(self, command, params, grid, parser):
        """
        Route system commands to appropriate handlers.

        Args:
            command: Command name (e.g., 'REPAIR', 'STATUS')
            params: List of command parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Command result string
        """
        # Map commands to handler methods
        handlers = {
            'BLANK': self.handle_blank,
            'SPLASH': self.handle_splash,
            'HELP': self.handle_help,
            'PROGRESS': self.handle_progress,
            'LAYOUT': self.handle_layout,
            'STATUS': self.handle_status,
            'REPAIR': self.handle_repair,
            'SHAKEDOWN': self.handle_shakedown,
            'TREE': self.handle_tree,
            'DISK': self.handle_disk,
            'REBOOT': self.handle_reboot,
            'DESTROY': self.handle_destroy,
            'VIEWPORT': self.handle_viewport,
            'PALETTE': self.handle_palette,
            'DASH': self.handle_dashboard,
            'DASHBOARD': self.handle_dashboard,
            'CLEAN': self.handle_clean,
            'CONFIG': self.handle_config,
            'WIZARD': self.handle_wizard,
            'SETUP': self.handle_settings,
            # WORKSPACE command removed - use file pickers
            'OUTPUT': self.handle_output,
            'SERVER': self.handle_output,
            'WEB': self.handle_output,
            'GET': self.handle_get,
            'SET': self.handle_set,
            'HISTORY': self.handle_history,
            'SESSION': self.handle_session,
            'RESTORE': self.handle_restore,
            'LOCATE': self.handle_locate,
            'DEV': self.handle_dev_mode,
            'ASSETS': self.handle_assets,
            'UNDO': self.handle_undo,
            'REDO': self.handle_redo,
            'MODE': self.handle_mode,
            'GHOST': self.handle_ghost_mode,
            'TOMB': self.handle_tomb_mode,
            'CRYPT': self.handle_crypt_mode,
        }

        handler = handlers.get(command)
        if handler:
            return handler(params, grid, parser)
        else:
            return self.get_message("ERROR_UNKNOWN_SYSTEM_COMMAND", command=command)

    def _create_custom_theme(self, theme_manager, name):
        """Create a custom theme (simplified for now)."""
        try:
            # For now, create a sample custom theme based on current theme
            current_scheme = theme_manager.get_current_scheme()
            success = theme_manager.create_custom_theme(name, current_scheme)

            if success:
                return theme_manager.format_text(f"🎨 Custom theme created: {name}", "success") + "\n💡 Use 'THEME SET custom-{name}' to activate"
            else:
                return theme_manager.format_text(f"❌ Failed to create theme: {name}", "error")
        except Exception as e:
            return f"❌ Error creating custom theme: {e}"

    def handle_repair(self, params, grid, parser):
        """System diagnostics and repair - delegates to RepairHandler."""
        return self._get_repair_handler().handle_repair(params, grid, parser)

    def handle_shakedown(self, params, grid, parser):
        """Comprehensive system validation test suite - delegates to ShakedownHandler."""
        return self._get_shakedown_handler().handle(params)

    def handle_tree(self, params, grid, parser):
        """Display folder structure tree (v1.2.12)."""
        from pathlib import Path
        
        # Parse options
        show_full = '--full' in params
        show_memory_only = '--memory' in params
        
        output = []
        output.append("═" * 70)
        output.append("📁 uDOS FOLDER STRUCTURE (v1.2.12)")
        output.append("═" * 70)
        
        root = Path.cwd()
        
        # Define v1.2.x structure with expected state
        structure = {
            'core/': {'required': True, 'description': 'Core system files'},
            'extensions/': {'required': True, 'description': 'Extension system'},
            'knowledge/': {'required': True, 'description': 'Knowledge library'},
            'memory/': {'required': True, 'description': 'User workspace'},
            'memory/ucode/': {'required': True, 'description': 'Distributable scripts'},
            'memory/ucode/tests/': {'required': True, 'description': 'Test suites (tracked)'},
            'memory/ucode/stdlib/': {'required': True, 'description': 'Standard library (tracked)'},
            'memory/ucode/examples/': {'required': True, 'description': 'Example scripts (tracked)'},
            'memory/ucode/adventures/': {'required': True, 'description': 'Adventure scripts (tracked)'},
            'memory/ucode/scripts/': {'required': True, 'description': 'User scripts (ignored)'},
            'memory/ucode/sandbox/': {'required': True, 'description': 'Experimental (ignored)'},
            'memory/workflows/': {'required': True, 'description': 'Workflow automation (ignored)'},
            'memory/system/': {'required': True, 'description': 'System config (ignored)'},
            'memory/bank/': {'required': True, 'description': 'Banking data (ignored)'},
            'memory/shared/': {'required': True, 'description': 'Community content (ignored)'},
            'memory/logs/': {'required': True, 'description': 'Session logs (ignored)'},
            'wiki/': {'required': True, 'description': 'Documentation'},
            'dev/': {'required': True, 'description': 'Development files'},
        }
        
        if show_memory_only:
            # Filter to only memory/ structure
            structure = {k: v for k, v in structure.items() if k.startswith('memory/')}
        
        # Display tree
        for folder_path, info in sorted(structure.items()):
            full_path = root / folder_path
            exists = full_path.exists()
            
            # Determine status and color
            if exists:
                if info['required']:
                    status = "🟢"
                    status_text = "OK"
                else:
                    status = "🟡"
                    status_text = "EXTRA"
            else:
                status = "🔴"
                status_text = "MISSING"
            
            # Count files if exists
            file_count = ""
            if exists and show_full:
                files = list(full_path.rglob('*'))
                file_count = f" ({len([f for f in files if f.is_file()])} files)"
            
            # Format indentation
            indent_level = folder_path.count('/')
            indent = "  " * indent_level
            
            output.append(f"{indent}{status} {folder_path:<40} {status_text:>10}{file_count}")
            
            if show_full and info.get('description'):
                output.append(f"{indent}   {info['description']}")
        
        output.append("")
        output.append("Legend:")
        output.append("  🟢 OK      - Folder exists and is required")
        output.append("  🔴 MISSING - Required folder not found")
        output.append("  🟡 EXTRA   - Non-required folder present")
        output.append("")
        output.append("Options:")
        output.append("  TREE --full    - Show file counts and descriptions")
        output.append("  TREE --memory  - Show only memory/ structure")
        output.append("")
        
        return "\n".join(output)
    
    def handle_disk(self, params, grid, parser):
        """
        DISK command - disk usage monitoring and management.
        
        Commands:
            DISK                - Show disk usage report with progress bars
            DISK STATUS         - Same as DISK
            DISK INFO           - Show device hardware information
            DISK SCAN           - Refresh device hardware stats
            DISK HEALTH         - Check disk and memory thresholds
            DISK PRESET <name>  - Set preset (minimal/compact/standard/full/extended)
            DISK LIMIT <path> <mb> - Set custom limit for path
            DISK EXPORT         - Export report to JSON file
        """
        from core.services.disk_monitor import DiskMonitor
        from core.services.device_manager import DeviceManager
        from datetime import datetime
        
        monitor = DiskMonitor(self.config)
        device_mgr = DeviceManager(self.config)
        
        if not params:
            # Show combined report: disk usage + device info
            usage = monitor.scan_all(use_cache=False)
            monitor.print_report(usage, show_bars=True)
            
            # Check warnings
            warnings = monitor.check_limits(usage)
            if warnings:
                print("\n⚠️  WARNINGS:")
                for warning in warnings:
                    print(f"  {warning}")
            
            # Show device hardware summary
            print("\n" + "=" * 60)
            print("💻 DEVICE HARDWARE")
            print("=" * 60)
            
            hardware = device_mgr.get_info('hardware')
            if hardware:
                cpu = hardware.get('cpu', {})
                memory = hardware.get('memory', {})
                storage = hardware.get('storage', {})
                
                # CPU info
                print(f"\n🖥️  CPU:")
                print(f"   Model: {cpu.get('model', 'Unknown')}")
                print(f"   Cores: {cpu.get('cores', '?')} ({cpu.get('threads', '?')} threads)")
                print(f"   Speed: {cpu.get('frequency_ghz', '?')}GHz")
                if 'usage_percent' in cpu:
                    usage_pct = cpu['usage_percent']
                    bar = self._make_progress_bar(usage_pct, 20)
                    print(f"   Usage: {bar} {usage_pct:.1f}%")
                
                # Memory info
                print(f"\n💾 RAM:")
                total_gb = memory.get('total_gb', 0)
                available_gb = memory.get('available_gb', 0)
                used_pct = memory.get('used_percent', 0)
                bar = self._make_progress_bar(used_pct, 20)
                print(f"   Total: {total_gb:.1f}GB")
                print(f"   Available: {available_gb:.1f}GB")
                print(f"   Usage: {bar} {used_pct:.1f}%")
                
                # Storage info
                print(f"\n💿 Storage:")
                total_gb = storage.get('total_gb', 0)
                available_gb = storage.get('available_gb', 0)
                used_pct = storage.get('used_percent', 0)
                bar = self._make_progress_bar(used_pct, 20)
                print(f"   Total: {total_gb:.1f}GB ({storage.get('filesystem', '?')})")
                print(f"   Available: {available_gb:.1f}GB")
                print(f"   Usage: {bar} {used_pct:.1f}%")
            
            # Show location
            location = device_mgr.get_info('location')
            if location:
                print(f"\n📍 Location:")
                print(f"   Timezone: {location.get('timezone', '?')} ({location.get('timezone_abbr', '?')})")
                print(f"   TILE: {location.get('tile_code', '?')} ({location.get('city', '?')}, {location.get('country', '?')})")
            
            # Show suggestions
            suggestions = monitor.get_optimization_suggestions(usage)
            if suggestions:
                print("\n💡 OPTIMIZATION SUGGESTIONS:")
                for suggestion in suggestions:
                    print(f"  • {suggestion}")
            
            return ""
        
        subcommand = params[0].upper()
        
        if subcommand == 'STATUS':
            # Same as DISK with no params
            return self.handle_disk([], grid, parser)
        
        elif subcommand == 'PRESET':
            if len(params) < 2:
                # Show available presets
                output = [
                    "",
                    "📦 DISK PRESETS - Scalable uDOS Distributions",
                    "=" * 60,
                    "",
                    "Available presets:",
                    "",
                    "  minimal   (16MB)  - Core only, no extensions",
                    "  compact   (32MB)  - Core + essential extensions",
                    "  standard  (64MB)  - Core + extensions, limited knowledge",
                    "  full      (128MB) - Core + extensions + knowledge",
                    "  extended  (256MB+)- Everything + user data",
                    "",
                    f"Current preset: {self.config.get('disk_preset', 'custom').upper()}",
                    "",
                    "Usage: DISK PRESET <name>",
                    "=" * 60,
                ]
                return "\n".join(output)
            
            preset = params[1].lower()
            if monitor.set_preset(preset):
                return f"✅ Disk preset set to: {preset.upper()}\n💡 Run DISK to see new limits"
            else:
                return f"❌ Unknown preset: {preset}\n💡 Use: minimal, compact, standard, full, extended"
        
        elif subcommand == 'LIMIT':
            if len(params) < 3:
                return "Usage: DISK LIMIT <path> <mb>\nPaths: core, extensions, knowledge, memory, total"
            
            path = params[1].lower()
            try:
                limit_mb = float(params[2])
                monitor.set_custom_limit(path, limit_mb)
                return f"✅ Set {path} limit to {limit_mb}MB\n💡 Run DISK to see updated report"
            except ValueError:
                return f"❌ Invalid limit: {params[2]} (must be a number)"
        
        elif subcommand == 'INFO':
            # Show detailed device information
            print("=" * 60)
            print("💻 DEVICE INFORMATION")
            print("=" * 60)
            
            # Device identity
            device_info = device_mgr.get_info('device')
            if device_info:
                print(f"\n🖥️  Device:")
                print(f"   ID: {device_info.get('id', 'unknown')}")
                print(f"   Name: {device_info.get('name', 'Unknown Device')}")
                print(f"   Type: {device_info.get('type', 'unknown')}")
                print(f"   Platform: {device_info.get('platform', 'unknown')}")
                print(f"   Architecture: {device_info.get('architecture', 'unknown')}")
            
            # System info
            system_info = device_mgr.get_info('system')
            if system_info:
                print(f"\n⚙️  System:")
                print(f"   OS: {system_info.get('os', 'Unknown')} {system_info.get('version', '')}")
                print(f"   Kernel: {system_info.get('kernel', 'Unknown')}")
                print(f"   Hostname: {system_info.get('hostname', 'Unknown')}")
                uptime_hrs = system_info.get('uptime_hours', 0)
                uptime_days = uptime_hrs / 24
                print(f"   Uptime: {uptime_days:.1f} days ({uptime_hrs:.1f} hours)")
                print(f"   Python: {system_info.get('python_version', 'Unknown')}")
            
            # Hardware summary
            hardware = device_mgr.get_info('hardware')
            if hardware:
                cpu = hardware.get('cpu', {})
                memory = hardware.get('memory', {})
                storage = hardware.get('storage', {})
                
                print(f"\n🔧 Hardware:")
                print(f"   CPU: {cpu.get('model', 'Unknown')} ({cpu.get('cores', '?')} cores, {cpu.get('frequency_ghz', '?')}GHz)")
                print(f"   RAM: {memory.get('total_gb', '?')}GB (DDR4/DDR5)")
                print(f"   Storage: {storage.get('total_gb', '?')}GB {storage.get('filesystem', 'Unknown')}")
                display = hardware.get('display', {})
                if display:
                    print(f"   Display: {display.get('width', '?')}x{display.get('height', '?')} ({display.get('dpi', '?')}dpi)")
            
            # Network info
            network_info = device_mgr.get_info('network')
            if network_info:
                print(f"\n🌐 Network:")
                print(f"   Hostname: {network_info.get('hostname', 'Unknown')}")
                interfaces = network_info.get('interfaces', [])
                for iface in interfaces[:2]:  # Show first 2 interfaces
                    print(f"   {iface.get('name', '?')}: {iface.get('ipv4', 'No IPv4')} ({iface.get('status', 'unknown')})")
                if network_info.get('dns_servers'):
                    dns_list = ', '.join(network_info['dns_servers'][:2])
                    print(f"   DNS: {dns_list}")
            
            # Location
            location = device_mgr.get_info('location')
            if location:
                print(f"\n📍 Location:")
                print(f"   Timezone: {location.get('timezone', 'Unknown')} ({location.get('timezone_abbr', '?')})")
                print(f"   Offset: UTC{location.get('timezone_offset', '?')}")
                print(f"   TILE: {location.get('tile_code', 'Unknown')}")
                print(f"   City: {location.get('city', 'Unknown')}, {location.get('country', 'Unknown')}")
            
            # Capabilities
            capabilities = device_mgr.get_info('capabilities')
            if capabilities:
                print(f"\n✨ Capabilities:")
                cap_str = []
                if capabilities.get('audio'): cap_str.append("🔊 Audio")
                if capabilities.get('video'): cap_str.append("📹 Video")
                if capabilities.get('network'): cap_str.append("🌐 Network")
                if capabilities.get('bluetooth'): cap_str.append("📱 Bluetooth")
                if capabilities.get('virtualization'): cap_str.append("🖥️  Virtualization")
                if capabilities.get('containers'): cap_str.append("🐳 Containers")
                print(f"   {' │ '.join(cap_str)}")
            
            return ""
        
        elif subcommand == 'SCAN':
            # Refresh device hardware stats
            print("🔄 Scanning device hardware...")
            device_mgr.refresh()
            device_mgr.save()
            print("✅ Device information updated")
            print("\n💡 Run DISK or DISK INFO to see updated stats")
            return ""
        
        elif subcommand == 'HEALTH':
            # Check disk and memory health
            print("=" * 60)
            print("🏥 DEVICE HEALTH CHECK")
            print("=" * 60)
            
            health = device_mgr.check_health()
            
            # Disk health
            disk = health.get('disk', {})
            disk_status = disk.get('status', 'unknown')
            disk_icon = "✅" if disk_status == 'ok' else "⚠️"
            print(f"\n💿 Disk: {disk_icon} {disk_status.upper()}")
            print(f"   Usage: {disk.get('used_percent', 0):.1f}% ({disk.get('available_gb', 0):.1f}GB available)")
            print(f"   Threshold: {disk.get('threshold', 0):.0f}%")
            if disk_status == 'warning':
                print(f"   ⚠️  Disk usage above threshold!")
            
            # Memory health
            memory = health.get('memory', {})
            mem_status = memory.get('status', 'unknown')
            mem_icon = "✅" if mem_status == 'ok' else "⚠️"
            print(f"\n💾 Memory: {mem_icon} {mem_status.upper()}")
            print(f"   Usage: {memory.get('used_percent', 0):.1f}% ({memory.get('available_gb', 0):.1f}GB available)")
            print(f"   Threshold: {memory.get('threshold', 0):.0f}%")
            if mem_status == 'warning':
                print(f"   ⚠️  Memory usage above threshold!")
            
            # Overall status
            overall_status = "✅ HEALTHY" if disk_status == 'ok' and mem_status == 'ok' else "⚠️  ATTENTION NEEDED"
            print(f"\n📊 Overall: {overall_status}")
            
            return ""
        
        elif subcommand == 'EXPORT':
            # Export to memory/logs with uDOS filename format
            now = datetime.now()
            filename = now.strftime("%Y-%m-%d-%H-%M-%S") + "-disk-report.json"
            filepath = Path(self.config.project_root) / "memory" / "logs" / filename
            
            usage = monitor.scan_all(use_cache=False)
            monitor.export_report(filepath, usage)
            
            return f"✅ Disk report exported to:\n   {filepath.relative_to(self.config.project_root)}"
        
        else:
            return f"❌ Unknown DISK command: {subcommand}\n💡 Use: DISK [STATUS|INFO|SCAN|HEALTH|PRESET|LIMIT|EXPORT]"

    def handle_status(self, params, grid, parser):
        """Display comprehensive system status - delegates to DashboardHandler."""
        return self._get_dashboard_handler().handle_status(params, grid, parser)

    def handle_dashboard(self, params, grid, parser):
        """Display system dashboard - delegates to DashboardHandler."""
        return self._get_dashboard_handler().handle_dashboard(params, grid, parser)

    def handle_viewport(self, params, grid, parser):
        """Display viewport visualization - delegates to DashboardHandler."""
        return self._get_dashboard_handler().handle_viewport(params, grid, parser)

    def handle_palette(self, params, grid, parser):
        """Display color palette - delegates to DashboardHandler."""
        return self._get_dashboard_handler().handle_palette(params, grid, parser)

    def handle_settings(self, params, grid, parser):
        """Manage system settings - delegates to EnvironmentHandler."""
        return self.environment_handler.handle_settings(params, grid, parser)

    def handle_config(self, params, grid, parser):
        """Manage configuration files - supports CONFIG ROLE and delegates to ConfigurationHandler."""
        if params and params[0].upper() == 'ROLE':
            return self._handle_config_role(params[1:] if len(params) > 1 else [])
        return self._get_config_handler().handle_config(params, grid, parser)

    def _handle_config_role(self, params):
        """Handle CONFIG ROLE subcommand for wizard/dev role assignment."""
        if not params:
            # Show current role
            current_role = self.config_manager.get('USER_ROLE', 'user')
            return (f"📋 Current Role: {current_role}\n\n"
                   f"Available roles:\n"
                   f"  • user    - Standard user (default)\n"
                   f"  • wizard  - Developer access (OK DEV, advanced features)\n\n"
                   f"Usage: CONFIG ROLE <role>\n"
                   f"Example: CONFIG ROLE wizard")

        role = params[0].lower()
        if role not in ['user', 'wizard']:
            return f"❌ Invalid role: {role}\n💡 Available: user, wizard"

        # Set role in config
        self.config_manager.set('USER_ROLE', role)

        emoji = "🧙" if role == "wizard" else "👤"
        features = "\n✅ OK DEV enabled\n✅ Advanced system access" if role == "wizard" else ""

        return f"{emoji} Role set to: {role}{features}"

    # ======================================================================
    # CORE SYSTEM COMMANDS - Handled directly
    # ======================================================================

    def handle_reboot(self, params, grid, parser):
        """
        Restart the uDOS system or reload extensions.

        Variants:
            REBOOT                  - Full system restart
            REBOOT --extensions     - Reload all extensions (no core restart)
            REBOOT --extension <id> - Reload single extension
            REBOOT --validate       - Dry-run validation (no actual reload)

        Args:
            params: List with optional flags and extension ID
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Reboot status message or reload results
        """
        # Parse flags
        flags = [p for p in params if p.startswith('--')]
        args = [p for p in params if not p.startswith('--')]

        # Hot reload variants (v1.2.4+)
        if flags:
            return self._handle_hot_reload(flags, args)

        # Animated progress bar reboot (matches start_udos.sh)
        import time

        steps = [
            ("Saving state", "saved"),
            ("Clearing buffers", "cleared"),
            ("Viewport detection", None),  # Special handling
            ("Configuration", "ready"),
        ]

        # Show progress for each step
        for i, (step_name, completion_msg) in enumerate(steps, 1):
            print(self._show_progress(i, len(steps), f"{step_name}..."), end="", flush=True)
            time.sleep(0.15)

            # Clear line and show completion
            if i == 3:  # Viewport detection - SHOW EDUCATIONAL SPLASH
                try:
                    from core.services.viewport_manager import ViewportManager
                    from core.utils.viewport_viz import ViewportVisualizer
                    
                    vp = ViewportManager()
                    vp_info = vp.refresh_viewport()
                    tier = vp_info["screen_tier"]
                    size = f"{tier['actual_width_cells']}×{tier['actual_height_cells']}"
                    
                    # Show educational splash
                    print(f"\r{' ' * 80}\r\033[1;32m[✓]\033[0m {step_name:<20} ({size})  ", flush=True)
                    print("\n")
                    
                    # Create visualizer and show educational splash
                    viz = ViewportVisualizer(viewport=vp)
                    splash = viz.generate_educational_splash(viewport_manager=vp)
                    print(splash)
                    print("\n")
                    
                except Exception as e:
                    size = "cached"
                    print(f"\r{' ' * 80}\r\033[1;32m[✓]\033[0m {step_name:<20} ({size})  ", flush=True)
            else:
                print(f"\r{' ' * 80}\r\033[1;32m[✓]\033[0m {step_name:<20} ({completion_msg})  ", flush=True)

        # Final progress bar
        print(f"\r{' ' * 80}\r{self._show_progress(len(steps), len(steps), 'System ready!')}")
        print("\n\033[1;32m[✓]\033[0m All checks passed - restarting uDOS...\n")

        self.reboot_requested = True
        return ""

    def _show_progress(self, current, total, message):
        """Show animated progress bar matching startup style."""
        width = 35
        percentage = (current * 100) // total
        filled = (current * width) // total
        bar = "┌─ " + ("█" * filled) + ("░" * (width - filled)) + " ─┐"
        return f"\r{bar} \033[1;32m{percentage:3d}%\033[0m {message}"

    def _handle_hot_reload(self, flags, args):
        """
        Handle extension hot reload (REBOOT --extensions/--extension/--validate).

        Args:
            flags: List of flags (--extensions, --extension, --validate)
            args: List of arguments (extension ID for --extension)

        Returns:
            Reload result message
        """
        try:
            from core.services.extension_lifecycle import ExtensionLifecycleManager
            from core.services.extension_manager import ExtensionManager
        except ImportError as e:
            return f"❌ Hot reload not available: {e}\n💡 Falling back to full REBOOT\n"

        # Get extension manager instance
        try:
            ext_manager = ExtensionManager()
        except:
            ext_manager = None

        # Create lifecycle manager
        lifecycle = ExtensionLifecycleManager(ext_manager)

        # Determine mode
        validate_only = '--validate' in flags
        single_extension = '--extension' in flags
        all_extensions = '--extensions' in flags

        output = "\n"

        # Single extension reload
        if single_extension:
            if not args:
                return "❌ Error: --extension requires extension ID\n💡 Usage: REBOOT --extension <id>\n"

            ext_id = args[0]
            output += f"🔄 {'VALIDATING' if validate_only else 'RELOADING'} EXTENSION: {ext_id}\n\n"

            result = lifecycle.reload_extension(ext_id, validate_only)
            output += self._format_reload_result(result, validate_only)

        # All extensions reload
        elif all_extensions:
            output += f"🔄 {'VALIDATING' if validate_only else 'RELOADING'} ALL EXTENSIONS\n\n"

            results = lifecycle.reload_all_extensions(validate_only)
            for result in results:
                output += self._format_reload_result(result, validate_only)
                output += "\n"

        else:
            # Just --validate without --extension/--extensions
            return "❌ Error: --validate requires --extension <id> or --extensions\n💡 Usage: REBOOT --validate --extension <id>\n"

        return output

    def _format_reload_result(self, result, validate_only=False):
        """
        Format reload result for display.

        Args:
            result: ReloadResult object
            validate_only: Whether this was a validation-only run

        Returns:
            Formatted result string
        """
        from core.services.extension_lifecycle import ReloadResult

        if not isinstance(result, ReloadResult):
            return "❌ Invalid result format\n"

        output = ""

        if result.success:
            if validate_only:
                output += f"✅ Validation passed for '{result.extension_id}'\n"
                output += f"   📋 Extension is ready for reload\n"
            else:
                output += f"✅ Extension '{result.extension_id}' reloaded successfully!\n"
                if result.state_preserved:
                    output += f"   💾 State preserved\n"
                if result.modules_reloaded > 0:
                    output += f"   🔄 Modules reloaded: {result.modules_reloaded}\n"
                if result.commands_registered > 0:
                    output += f"   ⚡ Commands registered: {result.commands_registered}\n"
                output += f"   🚀 Changes are now active (no full restart needed)\n"
        else:
            output += f"❌ {result.message}\n"
            if result.errors:
                output += f"   📋 Errors:\n"
                for error in result.errors[:3]:  # Limit to 3 errors
                    # Shorten error messages
                    error_line = error.split('\n')[0][:80]
                    output += f"      • {error_line}\n"

        if result.warnings:
            output += f"   ⚠️  Warnings:\n"
            for warning in result.warnings[:3]:  # Limit to 3 warnings
                output += f"      • {warning}\n"

        return output

    def handle_destroy(self, params, grid, parser):
        """Destructive reset command with safety confirmations."""
        from core.commands.sandbox_handler import SandboxHandler

        destruction_type = params[0] if params else None

        # Map valid flags to modes
        mode_map = {"--reset": "reset", "--env": "env", "--all": "all"}

        if not destruction_type or destruction_type not in mode_map:
            return ("❌ DESTROY requires a flag\n\n"
                   "Available options:\n"
                   "  DESTROY --reset    Reset sandbox (safe - preserves user/tests)\n"
                   "  DESTROY --env      Clean environment files\n"
                   "  DESTROY --all      Delete all sandbox data (DANGER!)\n\n"
                   "⚠️  All DESTROY operations require confirmation")

        # Execute via sandbox handler
        return SandboxHandler().destroy_sandbox(mode=mode_map[destruction_type])

    # ======================================================================
    # STUB METHODS - To be implemented or moved to other handlers
    # ======================================================================

    def handle_clean(self, params, grid, parser):
        """Review sandbox files - delegates to EnvironmentHandler."""
        return self.environment_handler.handle_clean(params, grid, parser)

    def handle_wizard(self, params, grid, parser):
        """
        Enhanced setup wizard with multiple modes (renamed from SETUP).

        Modes:
        - WIZARD or WIZARD WIZARD: Full interactive wizard
        - WIZARD QUICK: Quick setup with sensible defaults
        - WIZARD THEME: Theme selection only
        - WIZARD VIEWPORT: Viewport configuration only
        - WIZARD EXTENSIONS: Extension management only
        - WIZARD HELP: Show setup help information
        """
        if not params:
            # Default to full wizard
            return self.setup_wizard.run_full_wizard()

        mode = params[0].upper()

        if mode == "HELP":
            return self.setup_wizard.format_help()

        elif mode == "WIZARD":
            return self.setup_wizard.run_full_wizard()

        elif mode == "QUICK":
            return self.setup_wizard.run_quick_setup()

        elif mode == "THEME":
            return self.setup_wizard.setup_theme_only()

        elif mode == "VIEWPORT":
            return self.setup_wizard.setup_viewport_only()

        elif mode == "EXTENSIONS":
            return self.setup_wizard.setup_extensions_only()

        else:
            return (f"❌ Unknown wizard mode: {mode}\n\n"
                   "📋 Available modes:\n"
                   "  WIZARD or WIZARD WIZARD     # Full interactive setup\n"
                   "  WIZARD QUICK              # Quick setup with defaults\n"
                   "  WIZARD THEME              # Theme selection only\n"
                   "  WIZARD VIEWPORT           # Viewport configuration only\n"
                   "  WIZARD EXTENSIONS         # Extension management only\n"
                   "  WIZARD HELP               # Show detailed help\n\n"
                   "💡 Tip: Use WIZARD HELP for detailed information\n"
                   "💡 Note: For settings, use SETUP or CONFIG commands")

    # WORKSPACE command removed - use file pickers with uDOS subdirectories instead
    # (sandbox, memory, knowledge, etc. act as workspaces)

    def handle_output(self, params, grid, parser):
        """Manage web servers and extensions - delegates to OutputHandler."""
        return self.output_handler.handle_output(params, grid, parser)

    def handle_get(self, params, grid, parser):
        """GET field value - delegates to VariableHandler."""
        return self.variable_handler.handle_get(params, grid, parser)

    def handle_set(self, params, grid, parser):
        """SET field value - delegates to VariableHandler."""
        return self.variable_handler.handle_set(params, grid, parser)

    def handle_history(self, params, grid, parser):
        """HISTORY command - show variable change history - delegates to VariableHandler."""
        return self.variable_handler.handle_history(params, grid, parser)

    def handle_session(self, params, grid, parser):
        """SESSION command - session management - delegates to SessionHandler."""
        return self._get_session_handler().handle_session(params, grid, parser)

    def handle_restore(self, params, grid, parser):
        """RESTORE command - restore to previous session - delegates to SessionHandler."""
        return self._get_session_handler().handle_restore(params, grid, parser)

    def _get_user_data(self):
        """Helper to get user data dictionary."""
        return {'username': getattr(self.user_manager, 'current_user', 'user') if self.user_manager else 'user'}

    def _format_cmd_result(self, result):
        """Helper to format command result with success/error prefix."""
        return result['message'] if result['success'] else f"❌ {result['message']}"

    # ═══════════════════════════════════════════════════════════════════════════
    # v1.2.22: ROLE-BASED PERMISSIONS SYSTEM
    # ═══════════════════════════════════════════════════════════════════════════

    def handle_role(self, params, grid, parser):
        """
        Handle ROLE commands - user role and permission management.
        
        Commands:
        - ROLE SETUP - First-time password setup (4-char min, 8+ recommended)
        - ROLE SET <level> - Change role (viewer/user/contributor/admin/wizard)
        - ROLE STATUS - Show current role and permissions
        - ROLE CHECK - Debug wizard detection
        
        Part of v1.2.22 - Self-Healing & Auto-Error-Awareness System
        """
        from core.services.role_manager import RoleManager, UserRole
        
        role_manager = RoleManager(self.config)
        
        if not params:
            return "Usage: ROLE SETUP|SET|STATUS|CHECK"
        
        subcommand = params[0].upper()
        
        if subcommand == 'SETUP':
            return self._handle_role_setup(role_manager)
        elif subcommand == 'SET':
            if len(params) < 2:
                return "Usage: ROLE SET <level>\nLevels: viewer, user, contributor, admin, wizard"
            return self._handle_role_set(role_manager, params[1])
        elif subcommand == 'STATUS':
            return self._handle_role_status(role_manager)
        elif subcommand == 'CHECK':
            return self._handle_role_check(role_manager)
        else:
            return f"Unknown ROLE command: {subcommand}\nUsage: ROLE SETUP|SET|STATUS|CHECK"
    
    def _handle_role_setup(self, role_manager):
        """Handle ROLE SETUP - first-time password setup."""
        import getpass
        
        print("\n🔐 Role Setup - Admin/Wizard Password Configuration")
        print("━" * 60)
        print("Create a password for admin/wizard access.")
        print("Minimum 4 characters, 8+ characters recommended.")
        print("Press Enter for no password (less secure).\n")
        
        try:
            password1 = getpass.getpass("Enter password: ")
            
            if password1:
                password2 = getpass.getpass("Confirm password: ")
                
                if password1 != password2:
                    return "❌ Passwords do not match. Setup cancelled."
                
                if len(password1) < 4:
                    return "❌ Password must be at least 4 characters."
                
                # Strength indicator
                strength = "weak" if len(password1) < 8 else "medium" if len(password1) < 12 else "strong"
                print(f"Password strength: {strength}")
            
            # Set password
            if role_manager.set_password(password1):
                status = "✅ Password saved to .env"
                if not password1:
                    status += " (no password required)"
                
                # Check wizard status
                if role_manager._detect_wizard():
                    status += "\n✨ Wizard role auto-detected from git author"
                
                return status
            else:
                return "❌ Failed to save password."
        
        except (EOFError, KeyboardInterrupt):
            return "\n❌ Setup cancelled."
    
    def _handle_role_set(self, role_manager, level_str):
        """Handle ROLE SET - change user role."""
        from core.services.role_manager import UserRole
        
        # Parse role level
        try:
            role = UserRole(level_str.lower())
        except ValueError:
            return f"❌ Invalid role: {level_str}\nValid roles: viewer, user, contributor, admin, wizard"
        
        # Check if password required
        if role in [UserRole.ADMIN, UserRole.WIZARD]:
            password = role_manager.prompt_password(f"Enter password for {role.value} access: ")
            if not password:
                return "❌ Password required for admin/wizard role."
        else:
            password = None
        
        # Set role
        if role_manager.set_role(role, password):
            return f"✅ Role changed to: {role.value}"
        else:
            if role == UserRole.WIZARD:
                return "❌ Wizard role requires git author match in CREDITS.md"
            else:
                return "❌ Failed to change role. Check password."
    
    def _handle_role_status(self, role_manager):
        """Handle ROLE STATUS - show current role and permissions."""
        info = role_manager.get_role_info()
        
        output = ["\n📋 Role Status"]
        output.append("━" * 60)
        output.append(f"Current Role: {info['role_name']} ({info['role']})")
        
        if info['wizard_detected']:
            output.append("✨ Wizard detected (git author matches CREDITS.md)")
        
        output.append("\nPermissions:")
        perms = info['permissions']
        output.append(f"  📖 Read knowledge: {'✅' if perms['read_knowledge'] else '❌'}")
        output.append(f"  ✍️  Write memory: {'✅' if perms['write_memory'] else '❌'}")
        output.append(f"  ⚙️  Run workflows: {'✅' if perms['run_workflows'] else '❌'}")
        output.append(f"  📤 Submit content: {'✅' if perms['submit_content'] else '❌'}")
        output.append(f"  🔧 Edit core: {'✅' if perms['edit_core'] else '❌'}")
        output.append(f"  🧩 Edit extensions: {'✅' if perms['edit_extensions'] else '❌'}")
        output.append(f"  🐛 DEV MODE: {'✅' if perms['dev_mode'] else '❌'}")
        output.append(f"  🧪 Sandbox testing: {'✅' if perms['sandbox_test'] else '❌'}")
        
        return "\n".join(output)
    
    def _handle_role_check(self, role_manager):
        """Handle ROLE CHECK - debug wizard detection."""
        info = role_manager.get_debug_info()
        
        output = ["\n🔍 Role Debug Information"]
        output.append("━" * 60)
        output.append(f"Current Role: {info['current_role']}")
        output.append(f"Wizard Detected: {'✅' if info['wizard_detected'] else '❌'}")
        output.append(f"\nGit Author: {info.get('git_author', 'Not found')}")
        
        if info.get('credits_emails'):
            output.append(f"\nCREDITS.md Emails ({len(info['credits_emails'])}):")
            for email in info['credits_emails'][:10]:  # Show first 10
                output.append(f"  • {email}")
            if len(info['credits_emails']) > 10:
                output.append(f"  ... and {len(info['credits_emails']) - 10} more")
        else:
            output.append("\nNo emails found in CREDITS.md")
        
        output.append(f"\nMatch Found: {'✅' if info.get('match_found') else '❌'}")
        
        if 'error' in info:
            output.append(f"\n⚠️  Error: {info['error']}")
        
        return "\n".join(output)

    # ═══════════════════════════════════════════════════════════════════════════
    # v1.2.22: ERROR PATTERN LEARNING SYSTEM
    # ═══════════════════════════════════════════════════════════════════════════

    def handle_patterns(self, params, grid, parser):
        """
        Handle PATTERNS commands - error pattern management.
        
        Commands:
        - PATTERNS STATUS - Show pattern learning statistics
        - PATTERNS CLEAR - Clear all learned patterns (requires confirmation)
        - PATTERNS EXPORT [file] - Export patterns to JSON file
        
        Part of v1.2.22 - Self-Healing & Auto-Error-Awareness System
        """
        from core.services.pattern_learner import get_pattern_learner
        from datetime import datetime
        
        learner = get_pattern_learner()
        
        if not params:
            return "Usage: PATTERNS STATUS|CLEAR|EXPORT"
        
        subcommand = params[0].upper()
        
        if subcommand == 'STATUS':
            return self._handle_patterns_status(learner)
        elif subcommand == 'CLEAR':
            return self._handle_patterns_clear(learner)
        elif subcommand == 'EXPORT':
            filename = params[1] if len(params) > 1 else None
            return self._handle_patterns_export(learner, filename)
        else:
            return f"Unknown PATTERNS command: {subcommand}\nUsage: PATTERNS STATUS|CLEAR|EXPORT"
    
    def _handle_patterns_status(self, learner):
        """Handle PATTERNS STATUS - show statistics."""
        stats = learner.get_statistics()
        
        output = ["\n📚 Error Pattern Learning Statistics"]
        output.append("━" * 60)
        output.append(f"Total Patterns: {stats['total_patterns']}")
        output.append(f"Total Occurrences: {stats['total_occurrences']}")
        output.append(f"Patterns with Fixes: {stats['patterns_with_fixes']}")
        
        if stats['average_success_rate'] > 0:
            output.append(f"Average Success Rate: {stats['average_success_rate']:.1f}%")
        
        # Privacy notice
        output.append("\n🔒 Privacy:")
        output.append("  • All data stored locally only")
        output.append("  • Usernames, paths, and keys are sanitized")
        output.append("  • No telemetry or cloud sync")
        output.append(f"  • Data location: memory/bank/system/error_patterns.json")
        
        # Recent patterns
        if stats['total_patterns'] > 0:
            output.append("\nRecent Patterns:")
            patterns_data = learner._load_patterns()
            recent = sorted(patterns_data.items(), key=lambda x: x[1].get('last_seen', ''), reverse=True)[:5]
            
            for signature, data in recent:
                error_type = data.get('error_type', 'Unknown')
                count = data.get('count', 0)
                fixes = len(data.get('suggested_fixes', []))
                output.append(f"  • {error_type} (#{signature[:8]}): {count}x, {fixes} fixes")
        
        output.append("\nCommands:")
        output.append("  • PATTERNS CLEAR - Clear all patterns")
        output.append("  • PATTERNS EXPORT - Export to JSON")
        output.append("  • OK FIX - Get fix suggestions for errors")
        
        return "\n".join(output)
    
    def _handle_patterns_clear(self, learner):
        """Handle PATTERNS CLEAR - clear all learned patterns."""
        import sys
        
        print("\n⚠️  WARNING: This will delete all learned error patterns!")
        print("This action cannot be undone.\n")
        
        try:
            response = input("Type 'yes' to confirm: ")
            if response.lower() == 'yes':
                learner.clear_patterns()
                return "✅ All error patterns cleared"
            else:
                return "❌ Clear cancelled"
        except (EOFError, KeyboardInterrupt):
            return "\n❌ Clear cancelled"
    
    def _handle_patterns_export(self, learner, filename=None):
        """Handle PATTERNS EXPORT - export patterns to JSON."""
        from datetime import datetime
        from pathlib import Path
        
        # Generate filename with uDOS format if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            filename = f"{timestamp}-error-patterns.json"
        
        # Export to memory/docs/
        output_dir = Path("memory/docs")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename
        
        try:
            learner.export_patterns(str(output_path))
            
            # Show file size
            size = output_path.stat().st_size
            size_str = f"{size} bytes" if size < 1024 else f"{size/1024:.1f} KB"
            
            return f"✅ Patterns exported to: {output_path}\nSize: {size_str}"
        
        except Exception as e:
            return f"❌ Export failed: {e}"

    def handle_error(self, params, grid, parser):
        """
        Handle ERROR commands - error context management.
        
        Commands:
        - ERROR HISTORY - Show recent errors
        - ERROR SHOW <signature> - Show full error details
        - ERROR CLEAR - Clear error history (requires confirmation)
        
        Part of v1.2.22 - Self-Healing & Auto-Error-Awareness System
        """
        from core.services.error_interceptor import get_error_context_manager
        
        error_manager = get_error_context_manager()
        
        if not params:
            return "Usage: ERROR HISTORY|SHOW|CLEAR"
        
        subcommand = params[0].upper()
        
        if subcommand == 'HISTORY':
            return self._handle_error_history(error_manager)
        elif subcommand == 'SHOW':
            if len(params) < 2:
                return "Usage: ERROR SHOW <signature>"
            signature = params[1].lstrip('#')  # Remove # prefix if present
            return self._handle_error_show(error_manager, signature)
        elif subcommand == 'CLEAR':
            return self._handle_error_clear(error_manager)
        else:
            return f"Unknown ERROR command: {subcommand}\nUsage: ERROR HISTORY|SHOW|CLEAR"
    
    def _handle_error_history(self, error_manager):
        """Handle ERROR HISTORY - show recent errors."""
        contexts = error_manager.get_all_contexts(limit=10)
        
        if not contexts:
            return "✅ No errors in history"
        
        output = ["\n🔍 Recent Error History"]
        output.append("━" * 60)
        
        for i, ctx in enumerate(contexts, 1):
            timestamp = ctx.get('timestamp', 'Unknown')
            error_type = ctx.get('error_type', 'Unknown')
            message = ctx.get('message', 'No message')[:50]  # Truncate
            signature = ctx.get('signature', 'N/A')
            severity = ctx.get('severity', 'MEDIUM')
            
            # Severity indicator
            indicator = '🔴' if severity == 'CRITICAL' else '🟡' if severity == 'HIGH' else '🟢'
            
            output.append(f"{i}. {indicator} {error_type} (#{signature[:8]})")
            output.append(f"   {message}...")
            output.append(f"   Time: {timestamp}")
            output.append("")
        
        output.append("Commands:")
        output.append("  • ERROR SHOW #<signature> - View full error details")
        output.append("  • OK FIX #<signature> - Get fix suggestions")
        output.append("  • ERROR CLEAR - Clear error history")
        
        return "\n".join(output)
    
    def _handle_error_show(self, error_manager, signature):
        """Handle ERROR SHOW - show full error details."""
        ctx = error_manager.get_context(signature)
        
        if not ctx:
            return f"❌ Error not found: #{signature}\n\nUse: ERROR HISTORY to see available errors"
        
        output = ["\n🔍 Error Details"]
        output.append("━" * 60)
        output.append(f"Type: {ctx.get('error_type', 'Unknown')}")
        output.append(f"Message: {ctx.get('message', 'No message')}")
        output.append(f"Signature: #{ctx.get('signature', 'N/A')}")
        output.append(f"Severity: {ctx.get('severity', 'MEDIUM')}")
        output.append(f"Timestamp: {ctx.get('timestamp', 'Unknown')}")
        
        if ctx.get('command'):
            output.append(f"Command: {ctx['command']}")
        
        if ctx.get('stack_trace'):
            output.append("\nStack Trace:")
            output.append(ctx['stack_trace'])
        
        if ctx.get('environment'):
            env = ctx['environment']
            output.append("\nEnvironment:")
            output.append(f"  Theme: {env.get('theme', 'Unknown')}")
            output.append(f"  Location: {env.get('tile_location', 'Unknown')}")
        
        output.append("\nNext Steps:")
        output.append(f"  • OK FIX #{signature[:8]} - Get fix suggestions")
        output.append("  • DEV MODE - Enter debug mode")
        
        return "\n".join(output)
    
    def _handle_error_clear(self, error_manager):
        """Handle ERROR CLEAR - clear error history."""
        import sys
        
        print("\n⚠️  WARNING: This will delete all error history!")
        print("This action cannot be undone.\n")
        
        try:
            response = input("Type 'yes' to confirm: ")
            if response.lower() == 'yes':
                error_manager.clear_all()
                return "✅ Error history cleared"
            else:
                return "❌ Clear cancelled"
        except (EOFError, KeyboardInterrupt):
            return "\n❌ Clear cancelled"

    # ═══════════════════════════════════════════════════════════════════════════
    # v1.0.32: PLANET SYSTEM COMMANDS (CONFIG PLANET deprecated v1.2.21)
    # ═══════════════════════════════════════════════════════════════════════════

    def handle_locate(self, params, grid, parser):
        """Handle LOCATE command - delegates to cmd_locate."""
        from core.commands.cmd_locate import cmd_locate
        return self._format_cmd_result(cmd_locate(self._get_user_data(), params))

    def handle_dev_mode(self, params, grid, parser):
        """Handle DEV MODE commands - delegates to EnvironmentHandler."""
        return self.environment_handler.handle_dev_mode(params, grid, parser)

    def handle_assets(self, params, grid, parser):
        """
        Handle ASSETS commands (v1.5.3+).

        Delegates to AssetsHandler for asset management operations.

        Commands:
        - ASSETS LIST [type] - List available assets
        - ASSETS SEARCH <query> - Search for assets
        - ASSETS INFO <name> - Show asset details
        - ASSETS PREVIEW <name> - Preview asset contents
        - ASSETS LOAD <name> - Load asset into memory
        - ASSETS STATS - Show asset statistics
        - ASSETS RELOAD <name> - Hot-reload asset
        - ASSETS HELP - Show help

        Args:
            params: Command parameters
            grid: Grid object
            parser: Parser object

        Returns:
            Command response
        """
        from core.commands.assets_handler import handle_assets_command
        return handle_assets_command(params, grid, parser)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # v1.2.23: HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _make_progress_bar(self, percent: float, width: int = 20) -> str:
        """
        Create a progress bar visualization.
        
        Args:
            percent: Percentage (0-100)
            width: Width of bar in characters
        
        Returns:
            Progress bar string (e.g., "[▓▓▓▓▓▓▓░░░]")
        """
        filled = int((percent / 100) * width)
        empty = width - filled
        return f"[{'▓' * filled}{'░' * empty}]"
    
    def handle_undo(self, params, grid, parser):
        """
        Handle UNDO command - delegates to UndoHandler (v1.2.23).
        
        Commands:
        - UNDO <file> - Revert file to previous version
        - UNDO --list <file> - List version history
        - UNDO --to-version <version> <file> - Revert to specific version
        
        Args:
            params: Command parameters
            grid: Grid object
            parser: Parser object
            
        Returns:
            Command response
        """
        from core.commands.undo_handler import create_handler
        undo_handler = create_handler(
            viewport=self.viewport,
            logger=self.logger,
            output_formatter=self.output_formatter,
            parser=parser
        )
        return undo_handler.handle(params, grid, parser)
    
    def handle_redo(self, params, grid, parser):
        """
        Handle REDO command - delegates to UndoHandler (v1.2.23).
        
        Commands:
        - REDO <file> - Re-apply undone changes
        
        Args:
            params: Command parameters
            grid: Grid object
            parser: Parser object
            
        Returns:
            Command response
        """
        from core.commands.undo_handler import create_handler
        undo_handler = create_handler(
            viewport=self.viewport,
            logger=self.logger,
            output_formatter=self.output_formatter,
            parser=parser
        )
        return undo_handler.handle_redo(params, grid, parser)
        """Handle MODE command for switching prompt modes.
