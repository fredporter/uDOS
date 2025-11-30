"""
Schedule Command Handler for uDOS v1.1.2
Handles all SCHEDULE-related commands for task automation.

Commands:
- SCHEDULE DAILY AT <time> <command>
- SCHEDULE EVERY <interval> <unit> <command>
- SCHEDULE ONCE AT <datetime> <command>
- SCHEDULE WHEN <condition> <command>
- SCHEDULE STATUS [task_id]
- SCHEDULE LIST [--status=pending] [--priority=high] [--mission=id]
- SCHEDULE CANCEL <task_id>
- SCHEDULE PAUSE <task_id>
- SCHEDULE RESUME <task_id>
"""

import re
from datetime import datetime
from typing import Optional, List
from core.services.scheduler import (
    get_scheduler, ScheduleType, TaskPriority, TaskStatus
)


def handle_schedule_command(command_line: str) -> str:
    """
    Handle SCHEDULE commands.

    Args:
        command_line: Full command line (e.g., "SCHEDULE DAILY AT 09:00 [MISSION|STATUS*my-mission]")

    Returns:
        Command result message
    """
    # Parse command
    parts = command_line.strip().split(maxsplit=2)

    if len(parts) < 2:
        return _show_help()

    subcommand = parts[1].upper()
    args = parts[2] if len(parts) > 2 else ""

    scheduler = get_scheduler()

    # Route to appropriate handler
    if subcommand == "HELP":
        return _show_help()

    elif subcommand == "DAILY":
        return _handle_daily(args, scheduler)

    elif subcommand == "EVERY":
        return _handle_every(args, scheduler)

    elif subcommand == "ONCE":
        return _handle_once(args, scheduler)

    elif subcommand == "WHEN":
        return _handle_when(args, scheduler)

    elif subcommand == "STATUS":
        return _handle_status(args, scheduler)

    elif subcommand == "LIST":
        return _handle_list(args, scheduler)

    elif subcommand == "CANCEL":
        return _handle_cancel(args, scheduler)

    elif subcommand == "PAUSE":
        return _handle_pause(args, scheduler)

    elif subcommand == "RESUME":
        return _handle_resume(args, scheduler)

    else:
        return f"❌ Unknown SCHEDULE subcommand: {subcommand}\n💡 Use: SCHEDULE HELP"


def _handle_daily(args: str, scheduler) -> str:
    """Handle SCHEDULE DAILY AT command."""
    # Parse: AT <HH:MM> <command> [options]
    match = re.match(r'AT\s+(\d{1,2}:\d{2})\s+(.+)', args, re.IGNORECASE)
    if not match:
        return ("❌ Invalid DAILY syntax\n"
                "💡 Use: SCHEDULE DAILY AT <HH:MM> <command>\n"
                "   Example: SCHEDULE DAILY AT 09:00 [MISSION|STATUS*my-project]")

    time_str = match.group(1)
    command = match.group(2)

    # Validate time format
    try:
        hour, minute = map(int, time_str.split(':'))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError()
    except:
        return f"❌ Invalid time format: {time_str}\n💡 Use 24-hour format (HH:MM)"

    # Parse options
    priority, mission_id = _parse_options(command)
    command = _strip_options(command)

    # Generate task ID
    task_id = f"daily-{time_str.replace(':', '')}-{_generate_id()}"

    # Create task
    task = scheduler.create_task(
        task_id=task_id,
        name=f"Daily at {time_str}",
        command=command,
        schedule_type=ScheduleType.DAILY,
        schedule_config={'time': time_str},
        priority=priority,
        mission_id=mission_id
    )

    return (f"✅ Daily task scheduled: '{task.name}'\n"
            f"   ID: {task_id}\n"
            f"   Time: {time_str} daily\n"
            f"   Command: {command}\n"
            f"   Next run: {_format_datetime(task.next_run)}\n"
            f"   Priority: {_priority_icon(priority)}\n\n"
            f"💡 Manage: SCHEDULE STATUS {task_id}")


def _handle_every(args: str, scheduler) -> str:
    """Handle SCHEDULE EVERY command."""
    # Parse: <N> <unit> <command> [options]
    match = re.match(r'(\d+)\s+(second|minute|hour|day|week)s?\s+(.+)', args, re.IGNORECASE)
    if not match:
        return ("❌ Invalid EVERY syntax\n"
                "💡 Use: SCHEDULE EVERY <N> <unit> <command>\n"
                "   Units: seconds, minutes, hours, days, weeks\n"
                "   Example: SCHEDULE EVERY 30 minutes [KB|SEARCH*water]")

    value = int(match.group(1))
    unit = match.group(2).lower() + 's'  # Normalize to plural
    command = match.group(3)

    # Parse options
    priority, mission_id = _parse_options(command)
    command = _strip_options(command)

    # Generate task ID
    task_id = f"every-{value}{unit[0]}-{_generate_id()}"

    # Create task
    task = scheduler.create_task(
        task_id=task_id,
        name=f"Every {value} {unit}",
        command=command,
        schedule_type=ScheduleType.INTERVAL,
        schedule_config={'value': value, 'unit': unit},
        priority=priority,
        mission_id=mission_id
    )

    return (f"✅ Recurring task scheduled: '{task.name}'\n"
            f"   ID: {task_id}\n"
            f"   Interval: Every {value} {unit}\n"
            f"   Command: {command}\n"
            f"   Next run: {_format_datetime(task.next_run)}\n"
            f"   Priority: {_priority_icon(priority)}\n\n"
            f"💡 Manage: SCHEDULE STATUS {task_id}")


def _handle_once(args: str, scheduler) -> str:
    """Handle SCHEDULE ONCE AT command."""
    # Parse: AT <datetime> <command> [options]
    match = re.match(r'AT\s+(.+?)\s+(\[.+)', args, re.IGNORECASE)
    if not match:
        return ("❌ Invalid ONCE syntax\n"
                "💡 Use: SCHEDULE ONCE AT <datetime> <command>\n"
                "   Format: YYYY-MM-DD HH:MM or 'tomorrow 14:00'\n"
                "   Example: SCHEDULE ONCE AT 2025-12-01 10:00 [MISSION|START*project]")

    datetime_str = match.group(1).strip()
    command = match.group(2)

    # Parse datetime
    try:
        target_dt = _parse_datetime(datetime_str)
        if target_dt <= datetime.now():
            return f"❌ Datetime must be in the future: {datetime_str}"
    except Exception as e:
        return f"❌ Invalid datetime: {datetime_str}\n💡 {str(e)}"

    # Parse options
    priority, mission_id = _parse_options(command)
    command = _strip_options(command)

    # Generate task ID
    task_id = f"once-{_generate_id()}"

    # Create task
    task = scheduler.create_task(
        task_id=task_id,
        name=f"Once at {_format_datetime(target_dt.isoformat())}",
        command=command,
        schedule_type=ScheduleType.ONCE,
        schedule_config={'datetime': target_dt.isoformat()},
        priority=priority,
        mission_id=mission_id
    )

    return (f"✅ One-time task scheduled: '{task.name}'\n"
            f"   ID: {task_id}\n"
            f"   Run time: {_format_datetime(target_dt.isoformat())}\n"
            f"   Command: {command}\n"
            f"   Priority: {_priority_icon(priority)}\n\n"
            f"💡 Manage: SCHEDULE STATUS {task_id}")


def _handle_when(args: str, scheduler) -> str:
    """Handle SCHEDULE WHEN command."""
    # Parse: <condition> <command> [options]
    # For now, simplified condition syntax
    match = re.match(r'(.+?)\s+(\[.+)', args)
    if not match:
        return ("❌ Invalid WHEN syntax\n"
                "💡 Use: SCHEDULE WHEN <condition> <command>\n"
                "   Example: SCHEDULE WHEN file_exists:output.txt [MISSION|COMPLETE*analysis]")

    condition = match.group(1).strip()
    command = match.group(2)

    # Parse options
    priority, mission_id = _parse_options(command)
    command = _strip_options(command)

    # Generate task ID
    task_id = f"when-{_generate_id()}"

    # Create task
    task = scheduler.create_task(
        task_id=task_id,
        name=f"When: {condition[:30]}...",
        command=command,
        schedule_type=ScheduleType.CONDITION,
        schedule_config={'condition': condition},
        priority=priority,
        mission_id=mission_id
    )

    return (f"✅ Conditional task scheduled: '{task.name}'\n"
            f"   ID: {task_id}\n"
            f"   Condition: {condition}\n"
            f"   Command: {command}\n"
            f"   Priority: {_priority_icon(priority)}\n\n"
            f"⚠️  Note: Condition checking every 1 minute\n"
            f"💡 Manage: SCHEDULE STATUS {task_id}")


def _handle_status(args: str, scheduler) -> str:
    """Handle SCHEDULE STATUS command."""
    task_id = args.strip()

    if not task_id:
        # Show all active tasks
        tasks = scheduler.list_tasks(status=TaskStatus.PENDING.value)
        if not tasks:
            return "📋 No active scheduled tasks"

        lines = ["📋 Active Scheduled Tasks:\n"]
        for task in tasks[:10]:  # Limit to 10
            lines.append(_format_task_summary(task))

        if len(tasks) > 10:
            lines.append(f"\n... and {len(tasks) - 10} more")
            lines.append("💡 Use: SCHEDULE LIST for full list")

        return '\n'.join(lines)

    # Show specific task
    task = scheduler.get_task(task_id)
    if not task:
        return f"❌ Task not found: {task_id}"

    return _format_task_details(task)


def _handle_list(args: str, scheduler) -> str:
    """Handle SCHEDULE LIST command."""
    # Parse filters
    status_filter = None
    priority_filter = None
    mission_filter = None

    if '--status=' in args:
        match = re.search(r'--status=(\w+)', args)
        if match:
            status_filter = match.group(1)

    if '--priority=' in args:
        match = re.search(r'--priority=(\w+)', args)
        if match:
            priority_map = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4}
            priority_filter = priority_map.get(match.group(1).lower())

    if '--mission=' in args:
        match = re.search(r'--mission=(\S+)', args)
        if match:
            mission_filter = match.group(1)

    # Get filtered tasks
    tasks = scheduler.list_tasks(
        status=status_filter,
        mission_id=mission_filter,
        priority=priority_filter
    )

    if not tasks:
        return "📋 No scheduled tasks found"

    # Group by status
    grouped = {}
    for task in tasks:
        status = task.status.value
        if status not in grouped:
            grouped[status] = []
        grouped[status].append(task)

    lines = [f"📋 Scheduled Tasks ({len(tasks)} total):\n"]

    status_icons = {
        'pending': '⏳',
        'running': '🔄',
        'paused': '⏸️',
        'completed': '✅',
        'failed': '❌',
        'cancelled': '🚫'
    }

    for status, task_list in grouped.items():
        icon = status_icons.get(status, '📌')
        lines.append(f"\n{icon} {status.upper()}:")
        for task in task_list:
            lines.append(_format_task_summary(task))

    return '\n'.join(lines)


def _handle_cancel(args: str, scheduler) -> str:
    """Handle SCHEDULE CANCEL command."""
    task_id = args.strip()
    if not task_id:
        return "❌ Task ID required\n💡 Use: SCHEDULE CANCEL <task_id>"

    if scheduler.cancel_task(task_id):
        return f"✅ Task cancelled: {task_id}"
    else:
        return f"❌ Task not found: {task_id}"


def _handle_pause(args: str, scheduler) -> str:
    """Handle SCHEDULE PAUSE command."""
    task_id = args.strip()
    if not task_id:
        return "❌ Task ID required\n💡 Use: SCHEDULE PAUSE <task_id>"

    if scheduler.pause_task(task_id):
        return f"⏸️  Task paused: {task_id}"
    else:
        return f"❌ Task not found or cannot be paused: {task_id}"


def _handle_resume(args: str, scheduler) -> str:
    """Handle SCHEDULE RESUME command."""
    task_id = args.strip()
    if not task_id:
        return "❌ Task ID required\n💡 Use: SCHEDULE RESUME <task_id>"

    if scheduler.resume_task(task_id):
        return f"▶️  Task resumed: {task_id}"
    else:
        return f"❌ Task not found or cannot be resumed: {task_id}"


# Helper functions

def _parse_options(command: str) -> tuple:
    """Parse --priority and --mission options from command."""
    priority = TaskPriority.MEDIUM
    mission_id = None

    if '--priority=' in command:
        match = re.search(r'--priority=(critical|high|medium|low)', command, re.IGNORECASE)
        if match:
            priority_map = {
                'critical': TaskPriority.CRITICAL,
                'high': TaskPriority.HIGH,
                'medium': TaskPriority.MEDIUM,
                'low': TaskPriority.LOW
            }
            priority = priority_map.get(match.group(1).lower(), TaskPriority.MEDIUM)

    if '--mission=' in command:
        match = re.search(r'--mission=(\S+)', command)
        if match:
            mission_id = match.group(1)

    return priority, mission_id


def _strip_options(command: str) -> str:
    """Remove option flags from command string."""
    command = re.sub(r'\s*--priority=\S+', '', command)
    command = re.sub(r'\s*--mission=\S+', '', command)
    return command.strip()


def _generate_id() -> str:
    """Generate unique task ID suffix."""
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


def _parse_datetime(datetime_str: str) -> datetime:
    """Parse datetime string (supports various formats)."""
    # Try ISO format first
    try:
        return datetime.fromisoformat(datetime_str.replace(' ', 'T'))
    except:
        pass

    # Try common formats
    formats = [
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y %H:%M',
        '%m/%d/%Y %H:%M'
    ]

    for fmt in formats:
        try:
            return datetime.strptime(datetime_str, fmt)
        except:
            continue

    raise ValueError(f"Could not parse datetime: {datetime_str}")


def _format_datetime(iso_str: Optional[str]) -> str:
    """Format ISO datetime string for display."""
    if not iso_str:
        return "Not scheduled"

    dt = datetime.fromisoformat(iso_str)
    return dt.strftime('%Y-%m-%d %H:%M')


def _priority_icon(priority: TaskPriority) -> str:
    """Get emoji icon for priority."""
    icons = {
        TaskPriority.CRITICAL: '⚡ CRITICAL',
        TaskPriority.HIGH: '🔴 HIGH',
        TaskPriority.MEDIUM: '🟡 MEDIUM',
        TaskPriority.LOW: '🟢 LOW'
    }
    return icons.get(priority, '🟡 MEDIUM')


def _format_task_summary(task) -> str:
    """Format task as single-line summary."""
    priority_icons = {1: '⚡', 2: '🔴', 3: '🟡', 4: '🟢'}
    icon = priority_icons.get(task.priority.value, '🟡')

    next_run = _format_datetime(task.next_run) if task.next_run else 'N/A'

    return f"   {icon} {task.name} ({task.id}) - Next: {next_run}"


def _format_task_details(task) -> str:
    """Format complete task details."""
    status_icons = {
        TaskStatus.PENDING: '⏳',
        TaskStatus.RUNNING: '🔄',
        TaskStatus.PAUSED: '⏸️',
        TaskStatus.COMPLETED: '✅',
        TaskStatus.FAILED: '❌',
        TaskStatus.CANCELLED: '🚫'
    }

    lines = [
        f"\n{status_icons.get(task.status, '📌')} Task: {task.name}",
        f"   ID: {task.id}",
        f"   Status: {task.status.value.upper()}",
        f"   Priority: {_priority_icon(task.priority)}",
        f"   Schedule: {task.schedule_type.value}",
        f"   Command: {task.command}"
    ]

    if task.mission_id:
        lines.append(f"   Mission: {task.mission_id}")

    lines.append(f"   Next run: {_format_datetime(task.next_run)}")

    if task.last_run:
        lines.append(f"   Last run: {_format_datetime(task.last_run)}")

    if task.last_result:
        lines.append(f"   Last result: {task.last_result[:100]}...")

    if task.last_error:
        lines.append(f"   Last error: {task.last_error}")
        lines.append(f"   Retry count: {task.retry_count}/{task.max_retries}")

    if task.run_history:
        lines.append(f"\n📊 Run History ({len(task.run_history)} runs):")
        for run in task.run_history[-5:]:  # Last 5 runs
            timestamp = _format_datetime(run['timestamp'])
            status = run['status']
            lines.append(f"   • {timestamp} - {status}")

    return '\n'.join(lines)


def _show_help() -> str:
    """Show SCHEDULE command help."""
    return """📋 SCHEDULE Commands:

SCHEDULE DAILY AT <HH:MM> <command> [options]
   Run command daily at specific time (24-hour format)
   Example: SCHEDULE DAILY AT 09:00 [MISSION|STATUS*my-project]

SCHEDULE EVERY <N> <unit> <command> [options]
   Run command at regular intervals
   Units: seconds, minutes, hours, days, weeks
   Example: SCHEDULE EVERY 30 minutes [KB|SEARCH*water]

SCHEDULE ONCE AT <datetime> <command> [options]
   Run command once at specific datetime
   Format: YYYY-MM-DD HH:MM
   Example: SCHEDULE ONCE AT 2025-12-01 10:00 [MISSION|START*project]

SCHEDULE WHEN <condition> <command> [options]
   Run command when condition becomes true
   Example: SCHEDULE WHEN file_exists:output.txt [MISSION|COMPLETE*task]

SCHEDULE STATUS [task_id]
   Show task status (or all active tasks if no ID)

SCHEDULE LIST [--status=pending] [--priority=high] [--mission=id]
   List all scheduled tasks with optional filters

SCHEDULE CANCEL <task_id>
   Cancel a scheduled task

SCHEDULE PAUSE <task_id>
   Pause a scheduled task

SCHEDULE RESUME <task_id>
   Resume a paused task

Options:
  --priority=<critical|high|medium|low>  Set task priority
  --mission=<id>                          Link to mission

Examples:
  SCHEDULE DAILY AT 14:30 [MISSION|STATUS*novel] --priority=high
  SCHEDULE EVERY 2 hours [KB|SEARCH*survival] --mission=research
  SCHEDULE ONCE AT 2025-12-25 00:00 [PRINT|Merry Christmas!]
  SCHEDULE WHEN mission_complete:chapter-1 [MISSION|START*chapter-2]
"""


# Export main handler
__all__ = ['handle_schedule_command']
