"""
Resource Command Handler for uDOS

Provides user commands for resource monitoring and management:
- RESOURCE STATUS - View quota, disk, CPU, memory
- RESOURCE QUOTA [provider] - Check API quota for specific provider
- RESOURCE ALLOCATE mission_id --api N --disk M --priority P
- RESOURCE RELEASE mission_id
- RESOURCE THROTTLE mission_id [provider]
- RESOURCE SUMMARY - Complete resource dashboard
- RESOURCE HELP - Show command documentation

Author: uDOS Development Team
Version: 1.1.2
"""

from typing import Any, Dict, Optional

from core.services.resource_manager import get_resource_manager
from core.output.color_ui import ColorUI

# Initialize ColorUI for colored output
color_ui = ColorUI()


def handle_resource_command(command: str, **kwargs) -> Dict[str, Any]:
    """
    Main entry point for RESOURCE commands.

    Args:
        command: Resource subcommand (STATUS, QUOTA, ALLOCATE, etc.)
        **kwargs: Additional arguments from parser

    Returns:
        Dict with success status and result data
    """
    command_upper = command.upper()

    handlers = {
        'STATUS': _handle_status,
        'QUOTA': _handle_quota,
        'ALLOCATE': _handle_allocate,
        'RELEASE': _handle_release,
        'THROTTLE': _handle_throttle,
        'SUMMARY': _handle_summary,
        'HELP': _handle_help
    }

    handler = handlers.get(command_upper)
    if not handler:
        return {
            'success': False,
            'error': f'Unknown RESOURCE command: {command}',
            'hint': 'Try: RESOURCE HELP'
        }

    return handler(**kwargs)


def _handle_status(**kwargs) -> Dict[str, Any]:
    """
    Show resource status overview.

    Usage: RESOURCE STATUS
    """
    rm = get_resource_manager()

    # Get all resource info
    quotas = {
        'gemini': rm.check_api_quota('gemini'),
        'github': rm.check_api_quota('github')
    }
    disk = rm.get_disk_usage()
    system = rm.get_system_stats()

    # Format output
    lines = ["📊 Resource Status", "=" * 60, ""]

    # API Quotas
    lines.append("🔑 API Quotas:")
    for provider, info in quotas.items():
        if 'error' in info:
            continue

        emoji = "✅" if info['percent'] < 50 else "⚠️" if info['percent'] < 80 else "❌"
        lines.append(f"  {emoji} {provider.upper()}: {info['used']}/{info['limit']} ({info['percent']}%)")

    lines.append("")

    # Disk Space
    emoji = "✅" if disk['status'] == 'ok' else "⚠️" if disk['status'] == 'warning' else "❌"
    lines.append("💾 Disk Space:")
    lines.append(f"  {emoji} Sandbox: {disk['sandbox_mb']} MB")
    lines.append(f"  {emoji} System: {disk['used_mb']:.0f}/{disk['total_mb']:.0f} MB ({disk['percent']}%)")
    lines.append("")

    # System Resources
    cpu_emoji = "✅" if system['cpu_status'] == 'ok' else "⚠️" if system['cpu_status'] == 'warning' else "❌"
    mem_emoji = "✅" if system['memory_status'] == 'ok' else "⚠️" if system['memory_status'] == 'warning' else "❌"

    lines.append("⚡ System:")
    lines.append(f"  {cpu_emoji} CPU: {system['cpu_percent']}%")
    lines.append(f"  {mem_emoji} Memory: {system['memory_percent']}% ({system['memory_mb']:.0f} MB)")

    return {
        'success': True,
        'output': '\n'.join(lines),
        'data': {
            'quotas': quotas,
            'disk': disk,
            'system': system
        }
    }


def _handle_quota(provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Check API quota for specific provider.

    Usage: RESOURCE QUOTA [provider]
    """
    rm = get_resource_manager()

    if not provider:
        # Show all quotas
        providers = ['gemini', 'github']
    else:
        providers = [provider.lower()]

    lines = ["🔑 API Quotas", "=" * 60, ""]

    quota_data = {}
    for prov in providers:
        info = rm.check_api_quota(prov)
        quota_data[prov] = info

        if 'error' in info:
            lines.append(f"❌ {prov.upper()}: {info['error']}")
            continue

        # Status emoji
        emoji = "✅" if info['percent'] < 50 else "⚠️" if info['percent'] < 80 else "❌"

        lines.append(f"{emoji} {prov.upper()}")
        lines.append(f"   Used: {info['used']}/{info['limit']} calls ({info['percent']}%)")
        lines.append(f"   Available: {info['available']} calls")
        lines.append(f"   Resets at: {info['reset_at']}")
        lines.append("")

    return {
        'success': True,
        'output': '\n'.join(lines),
        'data': quota_data
    }


def _handle_allocate(
    mission_id: Optional[str] = None,
    api: int = 0,
    disk: int = 0,
    priority: str = 'MEDIUM',
    **kwargs
) -> Dict[str, Any]:
    """
    Allocate resources for a mission.

    Usage: RESOURCE ALLOCATE mission_id --api 100 --disk 500 --priority HIGH
    """
    if not mission_id:
        return {
            'success': False,
            'error': 'Mission ID required',
            'usage': 'RESOURCE ALLOCATE mission_id --api N --disk M --priority P'
        }

    rm = get_resource_manager()

    # Validate priority
    valid_priorities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
    priority_upper = priority.upper()
    if priority_upper not in valid_priorities:
        return {
            'success': False,
            'error': f'Invalid priority: {priority}',
            'hint': f'Valid priorities: {", ".join(valid_priorities)}'
        }

    # Attempt allocation
    success, message = rm.allocate_resources(mission_id, api, disk, priority_upper)

    if success:
        output = f"✅ Resources allocated for {mission_id}\n"
        output += f"   API calls: {api}\n"
        output += f"   Disk space: {disk} MB\n"
        output += f"   Priority: {priority_upper}"
    else:
        output = f"❌ Resource allocation failed\n   {message}"

    return {
        'success': success,
        'output': output,
        'message': message
    }


def _handle_release(mission_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Release resources allocated to a mission.

    Usage: RESOURCE RELEASE mission_id
    """
    if not mission_id:
        return {
            'success': False,
            'error': 'Mission ID required',
            'usage': 'RESOURCE RELEASE mission_id'
        }

    rm = get_resource_manager()
    rm.release_resources(mission_id)

    return {
        'success': True,
        'output': f"✅ Resources released for {mission_id}"
    }


def _handle_throttle(
    mission_id: Optional[str] = None,
    provider: str = 'gemini',
    **kwargs
) -> Dict[str, Any]:
    """
    Check if mission should be throttled.

    Usage: RESOURCE THROTTLE mission_id [provider]
    """
    if not mission_id:
        return {
            'success': False,
            'error': 'Mission ID required',
            'usage': 'RESOURCE THROTTLE mission_id [provider]'
        }

    rm = get_resource_manager()
    should_throttle, reason = rm.should_throttle(mission_id, provider)

    if should_throttle:
        output = f"⚠️ Throttling recommended for {mission_id}\n"
        output += f"   Reason: {reason}"
    else:
        output = f"✅ No throttling needed for {mission_id}"

    return {
        'success': True,
        'output': output,
        'throttle': should_throttle,
        'reason': reason
    }


def _handle_summary(**kwargs) -> Dict[str, Any]:
    """
    Show complete resource summary (dashboard view).

    Usage: RESOURCE SUMMARY
    """
    rm = get_resource_manager()
    summary = rm.get_resource_summary()

    lines = ["📊 Resource Summary Dashboard", "=" * 60, ""]

    # API Quotas Section
    lines.append("🔑 API Quotas:")
    for provider, info in summary['quotas'].items():
        if 'error' in info:
            continue

        emoji = "✅" if info['percent'] < 50 else "⚠️" if info['percent'] < 80 else "❌"
        bar = _create_progress_bar(info['percent'], width=30)
        lines.append(f"  {emoji} {provider.upper()}: {bar} {info['percent']}%")
        lines.append(f"     {info['used']}/{info['limit']} calls | Resets: {info['reset_at']}")

    lines.append("")

    # Disk Space Section
    disk = summary['disk']
    emoji = "✅" if disk['status'] == 'ok' else "⚠️" if disk['status'] == 'warning' else "❌"
    bar = _create_progress_bar(disk['percent'], width=30)

    lines.append("💾 Disk Space:")
    lines.append(f"  {emoji} System: {bar} {disk['percent']}%")
    lines.append(f"     Used: {disk['used_mb']:.0f} MB | Free: {disk['free_mb']:.0f} MB")
    lines.append(f"     Sandbox: {disk['sandbox_mb']} MB")

    lines.append("")

    # System Resources Section
    system = summary['system']
    cpu_emoji = "✅" if system['cpu_status'] == 'ok' else "⚠️" if system['cpu_status'] == 'warning' else "❌"
    mem_emoji = "✅" if system['memory_status'] == 'ok' else "⚠️" if system['memory_status'] == 'warning' else "❌"

    cpu_bar = _create_progress_bar(system['cpu_percent'], width=30)
    mem_bar = _create_progress_bar(system['memory_percent'], width=30)

    lines.append("⚡ System Resources:")
    lines.append(f"  {cpu_emoji} CPU: {cpu_bar} {system['cpu_percent']}%")
    lines.append(f"  {mem_emoji} Memory: {mem_bar} {system['memory_percent']}%")
    lines.append(f"     Used: {system['memory_mb']:.0f} MB")

    lines.append("")

    # Active Allocations Section
    if summary['allocations']:
        lines.append("🎯 Active Allocations:")
        for mission_id, alloc in summary['allocations'].items():
            priority_emoji = {
                'CRITICAL': '⚡',
                'HIGH': '🔥',
                'MEDIUM': '📊',
                'LOW': '🔧'
            }.get(alloc['priority'], '📊')

            lines.append(f"  {priority_emoji} {mission_id} ({alloc['priority']})")
            lines.append(f"     API: {alloc['api_calls']} calls | Disk: {alloc['disk_mb']} MB")
    else:
        lines.append("🎯 Active Allocations: None")

    return {
        'success': True,
        'output': '\n'.join(lines),
        'data': summary
    }


def _create_progress_bar(percent: float, width: int = 30) -> str:
    """Create ASCII progress bar."""
    filled = int(width * percent / 100)
    empty = width - filled

    # Color-coded bars (using unicode blocks)
    if percent < 50:
        fill_char = '█'  # Green (conceptually)
    elif percent < 80:
        fill_char = '▓'  # Yellow
    else:
        fill_char = '▒'  # Red

    empty_char = '░'

    return f"[{fill_char * filled}{empty_char * empty}]"


def _handle_help(**kwargs) -> Dict[str, Any]:
    """
    Show RESOURCE command help.

    Usage: RESOURCE(HELP)
    """
    # Build colored help text using ColorUI
    help_lines = []

    help_lines.append(color_ui.format("📊 RESOURCE Commands - Resource Monitoring & Management", 'cyan', bold=True))
    help_lines.append("")
    help_lines.append(color_ui.format("═" * 63, 'blue'))
    help_lines.append("")
    help_lines.append(color_ui.format("Commands:", 'yellow', bold=True))
    help_lines.append("")
    help_lines.append(color_ui.format("  RESOURCE(STATUS)", 'green', bold=True))
    help_lines.append("    Show overview of all resources (quotas, disk, CPU, memory)")
    help_lines.append("")
    help_lines.append(color_ui.format("  RESOURCE(QUOTA|provider)", 'green', bold=True))
    help_lines.append("    Check API quota for specific provider (gemini, github)")
    help_lines.append("    If no provider specified, shows all quotas")
    help_lines.append("")
    help_lines.append(color_ui.format("  RESOURCE(ALLOCATE|$MISSION_ID|--api N|--disk M|--priority P)", 'green', bold=True))
    help_lines.append("    Allocate resources for a mission")
    help_lines.append("")
    help_lines.append(color_ui.format("    Arguments:", 'yellow'))
    help_lines.append("      $MISSION_ID   Mission identifier")
    help_lines.append("      --api N       Number of API calls to reserve")
    help_lines.append("      --disk M      Disk space to reserve (MB)")
    help_lines.append("      --priority P  Priority level (CRITICAL, HIGH, MEDIUM, LOW)")
    help_lines.append("")
    help_lines.append(color_ui.format("    Example:", 'yellow'))
    help_lines.append("      RESOURCE(ALLOCATE|content-gen|--api 500|--disk 200|--priority HIGH)")
    help_lines.append("")
    help_lines.append(color_ui.format("  RESOURCE(RELEASE|$MISSION_ID)", 'green', bold=True))
    help_lines.append("    Release resources allocated to a mission")
    help_lines.append("")
    help_lines.append(color_ui.format("  RESOURCE(THROTTLE|$MISSION_ID|provider)", 'green', bold=True))
    help_lines.append("    Check if mission should be throttled due to resource constraints")
    help_lines.append("")
    help_lines.append(color_ui.format("    Arguments:", 'yellow'))
    help_lines.append("      $MISSION_ID Mission identifier")
    help_lines.append("      provider    API provider to check (default: gemini)")
    help_lines.append("")
    help_lines.append(color_ui.format("  RESOURCE(SUMMARY)", 'green', bold=True))
    help_lines.append("    Complete resource dashboard with progress bars")
    help_lines.append("    Shows quotas, disk, CPU, memory, and active allocations")
    help_lines.append("")
    help_lines.append(color_ui.format("  RESOURCE(HELP)", 'green', bold=True))
    help_lines.append("    Show this help message")
    help_lines.append("")
    help_lines.append(color_ui.format("═" * 63, 'blue'))
    help_lines.append("")
    help_lines.append(color_ui.format("Resource Types:", 'yellow', bold=True))
    help_lines.append("")
    help_lines.append(color_ui.format("  🔑 API Quotas", 'cyan'))
    help_lines.append("     - Daily/hourly limits per provider")
    help_lines.append("     - Auto-reset based on provider schedule")
    help_lines.append("     - Tracked per mission")
    help_lines.append("")
    help_lines.append(color_ui.format("  💾 Disk Space", 'cyan'))
    help_lines.append("     - Sandbox directory usage")
    help_lines.append("     - System disk usage")
    help_lines.append("     - Warning thresholds (80%, 90%)")
    help_lines.append("")
    help_lines.append(color_ui.format("  ⚡ System Resources", 'cyan'))
    help_lines.append("     - CPU usage monitoring")
    help_lines.append("     - Memory usage tracking")
    help_lines.append("     - Performance thresholds")
    help_lines.append("")
    help_lines.append(color_ui.format("═" * 63, 'blue'))
    help_lines.append("")
    help_lines.append(color_ui.format("Priority Levels:", 'yellow', bold=True))
    help_lines.append("")
    help_lines.append("  ⚡ CRITICAL  - Highest priority, can preempt others")
    help_lines.append("  🔥 HIGH      - High priority")
    help_lines.append("  📊 MEDIUM    - Default priority")
    help_lines.append("  🔧 LOW       - Lowest priority")
    help_lines.append("")
    help_lines.append("Higher priority missions can preempt lower priority missions when")
    help_lines.append("resources are constrained.")
    help_lines.append("")
    help_lines.append(color_ui.format("═" * 63, 'blue'))
    help_lines.append("")
    help_lines.append(color_ui.format("Status Indicators:", 'yellow', bold=True))
    help_lines.append("")
    help_lines.append("  ✅ OK        - Resource usage is healthy")
    help_lines.append("  ⚠️  WARNING  - Usage approaching limits")
    help_lines.append("  ❌ CRITICAL  - Usage at or exceeding limits")
    help_lines.append("")
    help_lines.append(color_ui.format("═" * 63, 'blue'))
    help_lines.append("")
    help_lines.append(color_ui.format("Examples:", 'yellow', bold=True))
    help_lines.append("")
    help_lines.append("  # Check all resources")
    help_lines.append("  RESOURCE(STATUS)")
    help_lines.append("")
    help_lines.append("  # Check Gemini API quota")
    help_lines.append("  RESOURCE(QUOTA|gemini)")
    help_lines.append("")
    help_lines.append("  # Allocate resources for content generation mission")
    help_lines.append("  RESOURCE(ALLOCATE|content-gen|--api 300|--disk 100|--priority HIGH)")
    help_lines.append("")
    help_lines.append("  # Check if mission should be throttled")
    help_lines.append("  RESOURCE(THROTTLE|content-gen)")
    help_lines.append("")
    help_lines.append("  # View complete dashboard")
    help_lines.append("  RESOURCE(SUMMARY)")
    help_lines.append("")
    help_lines.append("  # Release resources when mission completes")
    help_lines.append("  RESOURCE(RELEASE|content-gen)")
    help_lines.append("")
    help_lines.append(color_ui.format("═" * 63, 'blue'))

    return {
        'success': True,
        'output': '\n'.join(help_lines)
    }
