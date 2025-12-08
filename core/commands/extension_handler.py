"""
EXTENSION Command Handler v1.1.8
Provides interactive extension management, health monitoring, and performance dashboard.

Commands:
  EXTENSION LIST [category] - List all extensions (optionally filtered by category)
  EXTENSION INFO <id> - Show detailed extension information
  EXTENSION HEALTH [id] - Run health check on extension(s)
  EXTENSION DASHBOARD - Interactive health monitoring dashboard
  EXTENSION COMMANDS - Show all commands provided by extensions
  EXTENSION RELOAD - Reload all extension manifests
  EXTENSION VALIDATE <id> - Validate extension manifest
  EXTENSION METRICS [id] - Show performance metrics
  EXTENSION HELP - Show this help
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from core.services.extension_manager import (
    ExtensionManager,
    ExtensionMetadata,
    ExtensionStatus
)


class ExtensionCommandHandler:
    """Handler for EXTENSION commands."""

    def __init__(self, viewport=None, logger=None):
        """
        Initialize extension command handler.

        Args:
            viewport: Output viewport
            logger: Session logger
        """
        self.viewport = viewport
        self.logger = logger
        self.manager = ExtensionManager()

        # Auto-discover on init
        self.manager.discover_extensions(verbose=False)

    def handle_command(self, params: List[str]) -> str:
        """
        Route EXTENSION commands.

        Args:
            params: Command parameters

        Returns:
            Command result message
        """
        if not params or params[0].upper() == "HELP":
            return self._show_help()

        subcommand = params[0].upper()

        if subcommand == "LIST":
            category = params[1] if len(params) > 1 else None
            return self._list_extensions(category)

        elif subcommand == "INFO":
            if len(params) < 2:
                return "❌ Usage: EXTENSION INFO <extension_id>"
            return self._show_extension_info(params[1])

        elif subcommand == "HEALTH":
            ext_id = params[1] if len(params) > 1 else None
            return self._show_health(ext_id)

        elif subcommand == "DASHBOARD":
            return self._show_dashboard()

        elif subcommand == "COMMANDS":
            return self._show_commands_registry()

        elif subcommand == "RELOAD":
            return self._reload_extensions()

        elif subcommand == "VALIDATE":
            if len(params) < 2:
                return "❌ Usage: EXTENSION VALIDATE <extension_id>"
            return self._validate_extension(params[1])

        elif subcommand == "METRICS":
            ext_id = params[1] if len(params) > 1 else None
            return self._show_metrics(ext_id)

        else:
            return f"❌ Unknown subcommand: {subcommand}\n\n" + self._show_help()

    def _show_help(self) -> str:
        """Show EXTENSION command help."""
        return """
╔═══════════════════════════════════════════════════════════════╗
║                   EXTENSION COMMAND HELP                       ║
╚═══════════════════════════════════════════════════════════════╝

📦 EXTENSION MANAGEMENT

  LIST [category]         - List all extensions
                           Categories: core, bundled, native, cloned,
                                     play, web, cloud, api

  INFO <id>               - Show detailed extension information
  VALIDATE <id>           - Validate extension manifest

🏥 HEALTH & MONITORING

  HEALTH [id]             - Run health check (all or specific)
  DASHBOARD               - Interactive health monitoring dashboard
  METRICS [id]            - Show performance metrics

🔧 UTILITIES

  COMMANDS                - Show all commands provided by extensions
  RELOAD                  - Reload all extension manifests
  HELP                    - Show this help

📚 EXAMPLES

  EXTENSION LIST core             # List core extensions
  EXTENSION INFO teletext         # Show teletext extension details
  EXTENSION HEALTH                # Check health of all extensions
  EXTENSION DASHBOARD             # Open health dashboard
  EXTENSION COMMANDS              # Show command registry

═══════════════════════════════════════════════════════════════
"""

    def _list_extensions(self, category: Optional[str] = None) -> str:
        """List extensions with optional category filter."""
        extensions = self.manager.list_extensions(category=category)

        if not extensions:
            msg = "No extensions found"
            if category:
                msg += f" in category '{category}'"
            return f"ℹ️  {msg}"

        lines = []
        lines.append("\n📦 INSTALLED EXTENSIONS")
        lines.append("═" * 70)

        if category:
            lines.append(f"Category: {category}")
            lines.append("")

        # Group by category
        by_category = {}
        for ext in extensions:
            cat = ext.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(ext)

        for cat, exts in sorted(by_category.items()):
            lines.append(f"\n{cat.upper()} ({len(exts)})")
            lines.append("─" * 70)

            for ext in sorted(exts, key=lambda e: e.name):
                status_icon = self._get_status_icon(ext.status)
                lines.append(f"{status_icon} {ext.name} (v{ext.version})")
                lines.append(f"   ID: {ext.id}")
                lines.append(f"   {ext.description}")

                if ext.provides_commands:
                    cmd_count = len(ext.provides_commands)
                    cmd_names = [cmd.get('name', 'unknown') for cmd in ext.provides_commands[:3]]
                    cmd_str = ', '.join(cmd_names)
                    if cmd_count > 3:
                        cmd_str += f', +{cmd_count - 3} more'
                    lines.append(f"   Commands: {cmd_str}")

                lines.append("")

        lines.append(f"\nTotal: {len(extensions)} extension(s)")
        lines.append("═" * 70)

        return "\n".join(lines)

    def _show_extension_info(self, extension_id: str) -> str:
        """Show detailed information about an extension."""
        ext = self.manager.get_extension(extension_id)

        if not ext:
            return f"❌ Extension not found: {extension_id}"

        lines = []
        lines.append(f"\n📦 {ext.name} (v{ext.version})")
        lines.append("═" * 70)
        lines.append("")

        # Basic info
        lines.append(f"ID:          {ext.id}")
        lines.append(f"Author:      {ext.author}")
        lines.append(f"License:     {ext.license}")
        lines.append(f"Category:    {ext.category}")
        lines.append(f"Type:        {ext.type}")
        lines.append(f"Status:      {self._get_status_icon(ext.status)} {ext.status.value}")
        lines.append("")

        # Description
        lines.append(f"Description:")
        lines.append(f"  {ext.description}")
        lines.append("")

        # Location
        lines.append(f"Location:    {ext.extension_dir}")
        lines.append(f"Manifest:    {ext.manifest_path}")
        lines.append("")

        # Dependencies
        if ext.dependencies:
            lines.append("Dependencies:")
            for dep, version in ext.dependencies.items():
                lines.append(f"  • {dep}: {version}")
            lines.append("")

        # API Requirements
        if ext.requires_api:
            lines.append("Required APIs:")
            for api, config in ext.requires_api.items():
                lines.append(f"  • {api}")
                if isinstance(config, dict) and 'env_var' in config:
                    lines.append(f"    Environment: {config['env_var']}")
            lines.append("")

        # Commands
        if ext.provides_commands:
            lines.append(f"Provided Commands ({len(ext.provides_commands)}):")
            for cmd in ext.provides_commands:
                lines.append(f"  • {cmd.get('name', 'unknown')}")
                if 'description' in cmd:
                    lines.append(f"    {cmd['description']}")
            lines.append("")

        # Services
        if ext.provides_services:
            lines.append(f"Provided Services ({len(ext.provides_services)}):")
            for svc in ext.provides_services:
                lines.append(f"  • {svc.get('name', 'unknown')}")
                if 'description' in svc:
                    lines.append(f"    {svc['description']}")
            lines.append("")

        # API Endpoints
        if ext.provides_api_endpoints:
            lines.append(f"API Endpoints ({len(ext.provides_api_endpoints)}):")
            for endpoint in ext.provides_api_endpoints:
                method = endpoint.get('method', 'GET')
                path = endpoint.get('path', '/')
                lines.append(f"  • {method} {path}")
                if 'description' in endpoint:
                    lines.append(f"    {endpoint['description']}")
            lines.append("")

        # Configuration
        if ext.configuration:
            lines.append("Configuration:")
            for key, value in ext.configuration.items():
                lines.append(f"  {key}: {value}")
            lines.append("")

        # Health status
        if ext.last_health_check:
            lines.append(f"Last Health Check: {ext.last_health_check.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"Health Status: {ext.health_status}")
            if ext.last_error:
                lines.append(f"Last Error: {ext.last_error}")
            lines.append("")

        lines.append("═" * 70)

        return "\n".join(lines)

    def _show_health(self, extension_id: Optional[str] = None) -> str:
        """Show health check results."""
        if extension_id:
            # Check specific extension
            ext = self.manager.get_extension(extension_id)
            if not ext:
                return f"❌ Extension not found: {extension_id}"

            health_data = self.manager.check_health(extension_id)

            lines = []
            lines.append(f"\n🏥 Health Check: {ext.name}")
            lines.append("═" * 70)
            lines.append("")

            status_icon = "✅" if health_data['healthy'] else "❌"
            lines.append(f"Status: {status_icon} {health_data['status']}")

            if health_data.get('last_check'):
                lines.append(f"Last Check: {health_data['last_check']}")

            lines.append("")
            lines.append("═" * 70)

            return "\n".join(lines)
        else:
            # Check all extensions
            return self.manager.get_health_report()

    def _show_dashboard(self) -> str:
        """Show interactive health monitoring dashboard."""
        lines = []
        lines.append("\n╔═══════════════════════════════════════════════════════════════╗")
        lines.append("║          EXTENSION HEALTH MONITORING DASHBOARD                ║")
        lines.append("╚═══════════════════════════════════════════════════════════════╝")
        lines.append("")

        # Summary stats
        health_data = self.manager.check_health()
        total = health_data['total']
        healthy = health_data['healthy']
        unhealthy = health_data['unhealthy']

        health_percentage = (healthy / total * 100) if total > 0 else 0

        lines.append("📊 SYSTEM OVERVIEW")
        lines.append("─" * 70)
        lines.append(f"Total Extensions:     {total}")
        lines.append(f"Healthy:              {healthy} ✅")
        lines.append(f"Unhealthy:            {unhealthy} ❌")
        lines.append(f"Health Score:         {health_percentage:.1f}%")
        lines.append("")

        # Health bar
        bar_length = 50
        filled = int(bar_length * health_percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        lines.append(f"[{bar}] {health_percentage:.1f}%")
        lines.append("")

        # Category breakdown
        lines.append("📦 BY CATEGORY")
        lines.append("─" * 70)

        by_category = {}
        for ext in self.manager.list_extensions():
            cat = ext.category
            if cat not in by_category:
                by_category[cat] = {'total': 0, 'healthy': 0}
            by_category[cat]['total'] += 1

            # Check if healthy
            ext_health = health_data['extensions'].get(ext.id, {})
            if ext_health.get('healthy'):
                by_category[cat]['healthy'] += 1

        for cat, stats in sorted(by_category.items()):
            healthy_count = stats['healthy']
            total_count = stats['total']
            cat_percentage = (healthy_count / total_count * 100) if total_count > 0 else 0
            status = "✅" if cat_percentage == 100 else "⚠️" if cat_percentage >= 50 else "❌"

            lines.append(f"{status} {cat:12} {healthy_count}/{total_count} ({cat_percentage:.0f}%)")

        lines.append("")

        # Recent issues
        issues = []
        for ext_id, ext_health in health_data['extensions'].items():
            if not ext_health['healthy']:
                ext = self.manager.get_extension(ext_id)
                if ext:
                    issues.append((ext.name, ext_health['status']))

        if issues:
            lines.append("⚠️  ISSUES DETECTED")
            lines.append("─" * 70)
            for name, issue in issues[:5]:  # Show top 5
                lines.append(f"❌ {name}")
                lines.append(f"   {issue}")
            if len(issues) > 5:
                lines.append(f"   ... and {len(issues) - 5} more")
            lines.append("")

        lines.append("╚═══════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append("💡 Tip: Use 'EXTENSION HEALTH <id>' for detailed diagnostics")

        return "\n".join(lines)

    def _show_commands_registry(self) -> str:
        """Show all commands provided by extensions."""
        registry = self.manager.get_commands_registry()

        if not registry:
            return "ℹ️  No commands registered by extensions"

        lines = []
        lines.append("\n🔧 EXTENSION COMMAND REGISTRY")
        lines.append("═" * 70)
        lines.append("")

        # Group by category
        by_category = {}
        for cmd_name, cmd_info in registry.items():
            cat = cmd_info['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append((cmd_name, cmd_info))

        for cat, commands in sorted(by_category.items()):
            lines.append(f"\n{cat.upper()} ({len(commands)} commands)")
            lines.append("─" * 70)

            for cmd_name, cmd_info in sorted(commands):
                lines.append(f"• {cmd_name}")
                lines.append(f"  Extension: {cmd_info['extension_name']}")
                if cmd_info['description']:
                    lines.append(f"  {cmd_info['description']}")
                if cmd_info.get('syntax'):
                    lines.append(f"  Syntax: {cmd_info['syntax']}")
                lines.append("")

        lines.append(f"Total: {len(registry)} command(s)")
        lines.append("═" * 70)

        return "\n".join(lines)

    def _reload_extensions(self) -> str:
        """Reload all extension manifests."""
        count = self.manager.discover_extensions(verbose=False)

        return f"✅ Reloaded {count} extension(s)"

    def _validate_extension(self, extension_id: str) -> str:
        """Validate extension manifest."""
        ext = self.manager.get_extension(extension_id)

        if not ext:
            return f"❌ Extension not found: {extension_id}"

        # Re-validate manifest
        from core.services.extension_manager import ExtensionValidator

        try:
            with open(ext.manifest_path, 'r') as f:
                import json
                manifest = json.load(f)
        except Exception as e:
            return f"❌ Error reading manifest: {e}"

        is_valid, errors = ExtensionValidator.validate(manifest, ext.manifest_path)

        lines = []
        lines.append(f"\n🔍 Validation: {ext.name}")
        lines.append("═" * 70)
        lines.append("")

        if is_valid:
            lines.append("✅ Manifest is valid")
        else:
            lines.append("❌ Manifest validation failed:")
            lines.append("")
            for error in errors:
                lines.append(f"  • {error}")

        lines.append("")
        lines.append("═" * 70)

        return "\n".join(lines)

    def _show_metrics(self, extension_id: Optional[str] = None) -> str:
        """Show performance metrics."""
        lines = []
        lines.append("\n📈 PERFORMANCE METRICS")
        lines.append("═" * 70)
        lines.append("")

        if extension_id:
            # Show metrics for specific extension
            ext = self.manager.get_extension(extension_id)
            if not ext:
                return f"❌ Extension not found: {extension_id}"

            lines.append(f"Extension: {ext.name}")
            lines.append("")
            lines.append(f"Load Time:            {ext.load_time_ms:.2f} ms")
            lines.append(f"Total Invocations:    {ext.total_invocations}")
            lines.append(f"Avg Response Time:    {ext.avg_response_time_ms:.2f} ms")
            lines.append(f"Error Count:          {ext.error_count}")

            if ext.last_error:
                lines.append(f"Last Error:           {ext.last_error}")

        else:
            # Show summary metrics for all extensions
            all_exts = self.manager.list_extensions()

            total_invocations = sum(ext.total_invocations for ext in all_exts)
            avg_load_time = sum(ext.load_time_ms for ext in all_exts) / len(all_exts) if all_exts else 0
            total_errors = sum(ext.error_count for ext in all_exts)

            lines.append(f"Total Extensions:     {len(all_exts)}")
            lines.append(f"Total Invocations:    {total_invocations}")
            lines.append(f"Avg Load Time:        {avg_load_time:.2f} ms")
            lines.append(f"Total Errors:         {total_errors}")
            lines.append("")

            # Top performers
            lines.append("TOP 5 BY INVOCATIONS")
            lines.append("─" * 70)

            top_by_usage = sorted(all_exts, key=lambda e: e.total_invocations, reverse=True)[:5]

            for ext in top_by_usage:
                lines.append(f"{ext.name:20} {ext.total_invocations:8} calls  "
                           f"{ext.avg_response_time_ms:6.2f} ms avg")

        lines.append("")
        lines.append("═" * 70)
        lines.append("")
        lines.append("💡 Note: Metrics are collected when extensions are actively used")

        return "\n".join(lines)

    def _get_status_icon(self, status: ExtensionStatus) -> str:
        """Get status icon for extension."""
        icons = {
            ExtensionStatus.ACTIVE: "✅",
            ExtensionStatus.INACTIVE: "⏸️",
            ExtensionStatus.ERROR: "❌",
            ExtensionStatus.DISABLED: "🚫",
            ExtensionStatus.UNKNOWN: "❓"
        }
        return icons.get(status, "❓")


def create_extension_handler(viewport=None, logger=None) -> ExtensionCommandHandler:
    """Factory function to create extension command handler."""
    return ExtensionCommandHandler(viewport=viewport, logger=logger)
