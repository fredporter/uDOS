"""
Calendar Command Handler - v1.2.23 Task 4

Displays ASCII calendar views with task integration.
Uses demonstration layouts from memory/drafts/calendar_demos.py as reference.

Commands:
    CAL or CAL MONTH   - Show monthly calendar view
    CAL WEEK           - Show weekly calendar view
    CAL DAY or CAL TODAY - Show daily calendar view
    CAL NEXT           - Navigate to next month/week
    CAL PREV           - Navigate to previous month/week
    TASK LIST          - Show all tasks
    TASK ADD "<desc>" [--due DATE] [--urgent]  - Create new task
    TASK DONE <id>     - Mark task complete
    TASK DEL <id>      - Delete task
    TASK EDIT <id> <field> <value>  - Update task

Features:
- Timezone and TILE code display in headers
- Task indicators (📋 normal, ⚡ urgent, ✅ done)
- Progress bars for task completion
- Box-drawing characters for clean layout

Version: 1.2.23 (Calendar-Workflow)
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import calendar as cal_module
import json


class CalendarHandler:
    """Handler for calendar view commands."""
    
    def __init__(self, config, **kwargs):
        """
        Initialize calendar handler.
        
        Args:
            config: Config instance
            **kwargs: Additional handler dependencies
        """
        self.config = config
        self.current_date = datetime.now()
        self.view_mode = 'month'  # month, week, day
        
    @property
    def task_file(self):
        """Get path to tasks.json file."""
        return Path("memory/bank/user/tasks.json")
    
    def handle_command(self, params):
        """
        Handle CAL/CALENDAR and TASK commands.
        
        Args:
            params: Command parameters [command, ...args]
            
        Returns:
            Formatted output string
        """
        if not params:
            # Default: show monthly view
            return self._render_monthly_view()
        
        subcommand = params[0].upper()
        
        if subcommand in ['MONTH', 'MONTHLY']:
            self.view_mode = 'month'
            return self._render_monthly_view()
        
        elif subcommand in ['WEEK', 'WEEKLY']:
            self.view_mode = 'week'
            return self._render_weekly_view()
        
        elif subcommand in ['DAY', 'DAILY', 'TODAY']:
            self.view_mode = 'day'
            self.current_date = datetime.now()
            return self._render_daily_view()
        
        elif subcommand == 'NEXT':
            return self._navigate_next()
        
        elif subcommand == 'PREV':
            return self._navigate_previous()
        
        elif subcommand == 'LIST':
            return self._task_list()
        
        elif subcommand == 'ADD':
            return self._task_add(params[1:])
        
        elif subcommand == 'DONE':
            return self._task_done(params[1:])
        
        elif subcommand == 'DEL':
            return self._task_delete(params[1:])
        
        elif subcommand == 'EDIT':
            return self._task_edit(params[1:])
        
        else:
            return f"❌ Unknown CAL command: {subcommand}\n💡 Use: CAL [MONTH|WEEK|DAY|NEXT|PREV] or TASK [LIST|ADD|DONE|DEL|EDIT]"
    
    def _navigate_next(self) -> str:
        """Navigate to next time period."""
        if self.view_mode == 'month':
            # Next month
            if self.current_date.month == 12:
                self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month + 1)
            return self._render_monthly_view()
        
        elif self.view_mode == 'week':
            # Next week
            self.current_date += timedelta(days=7)
            return self._render_weekly_view()
        
        elif self.view_mode == 'day':
            # Next day
            self.current_date += timedelta(days=1)
            return self._render_daily_view()
        
        return ""
    
    def _navigate_previous(self) -> str:
        """Navigate to previous time period."""
        if self.view_mode == 'month':
            # Previous month
            if self.current_date.month == 1:
                self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month - 1)
            return self._render_monthly_view()
        
        elif self.view_mode == 'week':
            # Previous week
            self.current_date -= timedelta(days=7)
            return self._render_weekly_view()
        
        elif self.view_mode == 'day':
            # Previous day
            self.current_date -= timedelta(days=1)
            return self._render_daily_view()
        
        return ""
    
    def _get_timezone_info(self) -> tuple:
        """Get timezone abbreviation and offset."""
        # Get timezone from config or environment
        tz_name = self.config.get_env('TIMEZONE') or 'UTC'
        
        # Timezone abbreviation mapping
        tz_abbr_map = {
            'UTC': 'UTC',
            'America/New_York': 'EST',
            'America/Los_Angeles': 'PST',
            'Europe/London': 'GMT',
            'Europe/Paris': 'CET',
            'Asia/Tokyo': 'JST',
            'Australia/Sydney': 'AEST',
        }
        
        tz_abbr = tz_abbr_map.get(tz_name, 'UTC')
        
        # Calculate offset
        now = datetime.now()
        offset = now.astimezone().utcoffset()
        if offset:
            hours = int(offset.total_seconds() // 3600)
            offset_str = f"UTC{hours:+d}"
        else:
            offset_str = "UTC+0"
        
        return tz_abbr, offset_str
    
    def _get_tile_info(self) -> tuple:
        """Get TILE code and city name."""
        tile_code = self.config.get('tile_code', 'AA340')
        
        # Map TILE codes to cities (subset for demo)
        tile_city_map = {
            'AA340': 'Sydney',
            'JF57': 'London',
            'OP123': 'New York',
            'KL89': 'Tokyo',
            'MN45': 'Paris',
            'QR67': 'Berlin',
        }
        
        city = tile_city_map.get(tile_code, 'Unknown')
        return tile_code, city
    
    def _render_monthly_view(self) -> str:
        """Render monthly calendar view."""
        lines = []
        
        # Get timezone and location info
        tz_abbr, tz_offset = self._get_timezone_info()
        tile_code, city = self._get_tile_info()
        
        year = self.current_date.year
        month = self.current_date.month
        month_name = self.current_date.strftime("%B %Y").upper()
        
        # Header
        lines.append("╔" + "═" * 78 + "╗")
        lines.append(f"║{month_name.center(78)}║")
        lines.append(f"║{f'{tz_abbr} ({tz_offset})'.center(78)}║")
        lines.append(f"║{f'TILE: {tile_code} ({city})'.center(78)}║")
        lines.append("╠" + "═" * 78 + "╣")
        
        # Day headers
        day_headers = "║  SUN  │  MON  │  TUE  │  WED  │  THU  │  FRI  │  SAT  ║"
        lines.append(day_headers)
        lines.append("╠" + "═══════╪═══════╪═══════╪═══════╪═══════╪═══════╪═══════╣")
        
        # Get calendar month data
        month_cal = cal_module.monthcalendar(year, month)
        today = datetime.now()
        
        for week in month_cal:
            week_line = "║"
            for day in week:
                if day == 0:
                    week_line += "       │"
                else:
                    # Highlight current day
                    if day == today.day and month == today.month and year == today.year:
                        week_line += f" *{day:2d}*  │"
                    else:
                        week_line += f"  {day:2d}   │"
            
            # Remove last separator and add border
            week_line = week_line[:-1] + "║"
            lines.append(week_line)
            
            # Add empty line for task indicators
            lines.append("║" + "       │" * 6 + "       ║")
            
            # Separator between weeks
            if week != month_cal[-1]:
                lines.append("╠" + "───────┼───────┼───────┼───────┼───────┼───────┼───────╣")
        
        # Footer with legend
        lines.append("╚" + "═══════╧═══════╧═══════╧═══════╧═══════╧═══════╧═══════╝")
        lines.append("")
        lines.append("Legend:  *12* = Today  │  📋 = Task  │  ⚡ = Urgent  │  ✅ = Done")
        lines.append("")
        lines.append("💡 Commands: CAL NEXT | CAL PREV | CAL WEEK | CAL DAY")
        
        return "\n".join(lines)
    
    def _render_weekly_view(self) -> str:
        """Render weekly calendar view."""
        lines = []
        
        # Get timezone and location info
        tz_abbr, tz_offset = self._get_timezone_info()
        
        # Get week start (Monday)
        start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        week_num = start_of_week.isocalendar()[1]
        
        # Header
        lines.append("╔" + "═" * 78 + "╗")
        week_range = f"Week {week_num} - {start_of_week.strftime('%B %d')} to {(start_of_week + timedelta(days=6)).strftime('%B %d, %Y')}"
        lines.append(f"║{week_range.center(78)}║")
        lines.append(f"║{f'{tz_abbr} ({tz_offset})'.center(78)}║")
        lines.append("╠" + "═" * 78 + "╣")
        
        # Day columns header
        header = "║ TIME  │"
        for i in range(7):
            day = start_of_week + timedelta(days=i)
            day_str = day.strftime("%a %d")
            header += f" {day_str:6s} │"
        header = header[:-1] + "║"
        lines.append(header)
        lines.append("╠" + "═══════╪" + "════════╪" * 6 + "════════╣")
        
        # Time slots (6am to 8pm)
        for hour in range(6, 21):
            time_str = f"{hour:02d}:00"
            line = f"║ {time_str} │" + "        │" * 7
            line = line[:-1] + "║"
            lines.append(line)
        
        # Footer
        lines.append("╚" + "═══════╧" + "════════╧" * 6 + "════════╝")
        lines.append("")
        lines.append("💡 Commands: CAL NEXT | CAL PREV | CAL MONTH | CAL DAY")
        
        return "\n".join(lines)
    
    def _render_daily_view(self) -> str:
        """Render daily calendar view with split panel."""
        lines = []
        
        # Get timezone and location info
        tz_abbr, tz_offset = self._get_timezone_info()
        tile_code, city = self._get_tile_info()
        
        day_str = self.current_date.strftime("%A, %B %d, %Y").upper()
        time_str = datetime.now().strftime("%H:%M")
        
        # Header
        lines.append("╔" + "═" * 78 + "╗")
        lines.append(f"║{day_str.center(78)}║")
        lines.append(f"║{f'{time_str} {tz_abbr} ({tz_offset})'.center(78)}║")
        lines.append(f"║{f'TILE: {tile_code} ({city})'.center(78)}║")
        lines.append("╠" + "═" * 38 + "╤" + "═" * 39 + "╣")
        
        # Column headers
        lines.append("║" + " TIME BLOCKS".ljust(38) + "│" + " TASK LIST".ljust(39) + "║")
        lines.append("╠" + "═" * 38 + "╪" + "═" * 39 + "╣")
        
        # Hour rows (6am to midnight)
        current_hour = datetime.now().hour
        for hour in range(6, 24):
            time_str = f"{hour:02d}:00"
            
            # Time block visualization
            if hour == current_hour:
                block = "▓▓▓▓▓▓▓▓▓▓▓▓ ← NOW"
            elif hour < current_hour:
                block = "████████████"  # Past
            else:
                block = "░░░░░░░░░░░░"  # Future
            
            time_col = f" {time_str} {block}".ljust(38)
            
            # Task list column (placeholder)
            task_col = "".ljust(39)
            
            lines.append("║" + time_col + "│" + task_col + "║")
        
        # Footer with stats
        lines.append("╠" + "═" * 38 + "╧" + "═" * 39 + "╣")
        stats_line = " Energy: ▓▓▓▓▓▓▓░░░ 70%".ljust(38) + "│" + " Focus: ▓▓▓▓▓▓▓▓░░ 80%".ljust(39)
        lines.append("║" + stats_line + "║")
        lines.append("╚" + "═" * 78 + "╝")
        lines.append("")
        lines.append("Legend:  ████ Past  │  ▓▓▓▓ Now  │  ░░░░ Future")
        lines.append("")
        lines.append("💡 Commands: CAL NEXT | CAL PREV | CAL MONTH | CAL WEEK")
        
        return "\n".join(lines)
    
    # ======================== TASK MANAGEMENT METHODS ========================
    
    def _load_tasks(self) -> Dict:
        """Load tasks from tasks.json."""
        if not self.task_file.exists():
            return {"tasks": [], "next_id": 1}
        
        try:
            with open(self.task_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"tasks": [], "next_id": 1, "error": str(e)}
    
    def _save_tasks(self, data: Dict) -> bool:
        """Save tasks to tasks.json."""
        try:
            self.task_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.task_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving tasks: {e}")
            return False
    
    def _task_list(self) -> str:
        """List all tasks."""
        data = self._load_tasks()
        tasks = data.get("tasks", [])
        
        if not tasks:
            return "📋 No tasks yet. Use: TASK ADD \"description\" [--due DATE] [--urgent]"
        
        lines = []
        lines.append("╔" + "═" * 78 + "╗")
        lines.append("║" + " TASK LIST ".center(78) + "║")
        lines.append("╠" + "═" * 78 + "╣")
        
        for task in tasks:
            # Task header with ID and status
            status_icon = "✅" if task['status'] == 'done' else ("⚡" if task.get('priority') == 'urgent' else "📋")
            task_id = task['id']
            status = task['status'].upper()
            
            header = f"{status_icon} #{task_id} [{status}]"
            lines.append(f"║ {header:<76} ║")
            
            # Description
            desc = task['description']
            if len(desc) > 72:
                desc = desc[:69] + "..."
            lines.append(f"║   {desc:<74} ║")
            
            # Metadata line
            meta_parts = []
            if task.get('due_date'):
                meta_parts.append(f"Due: {task['due_date']}")
            if task.get('progress'):
                meta_parts.append(f"Progress: {task['progress']}%")
            if task.get('created'):
                meta_parts.append(f"Created: {task['created'][:10]}")
            
            if meta_parts:
                meta_line = " │ ".join(meta_parts)
                lines.append(f"║   {meta_line:<74} ║")
            
            # Progress bar if progress exists
            if task.get('progress'):
                progress = task['progress']
                filled = int(progress / 10)
                bar = "▓" * filled + "░" * (10 - filled)
                lines.append(f"║   [{bar}] {progress}%{' ' * (72 - len(bar) - len(str(progress)) - 6)}║")
            
            lines.append("╠" + "─" * 78 + "╣")
        
        # Replace last separator with bottom border
        lines[-1] = "╚" + "═" * 78 + "╝"
        
        # Add stats
        total = len(tasks)
        done = sum(1 for t in tasks if t['status'] == 'done')
        pending = total - done
        urgent = sum(1 for t in tasks if t.get('priority') == 'urgent' and t['status'] != 'done')
        
        lines.append("")
        lines.append(f"📊 Total: {total} │ ✅ Done: {done} │ 📋 Pending: {pending} │ ⚡ Urgent: {urgent}")
        lines.append("")
        lines.append("💡 Commands: TASK ADD \"desc\" | TASK DONE <id> | TASK DEL <id> | TASK EDIT <id> <field> <value>")
        
        return "\n".join(lines)
    
    def _task_add(self, params: List[str]) -> str:
        """Add a new task."""
        if not params:
            return "❌ Usage: TASK ADD \"description\" [--due DATE] [--urgent]"
        
        # Parse description (find quoted string)
        desc = None
        due_date = None
        is_urgent = False
        
        # Join params and parse
        full_text = " ".join(params)
        
        # Extract quoted description
        if '"' in full_text:
            parts = full_text.split('"')
            if len(parts) >= 2:
                desc = parts[1]
                remaining = parts[2] if len(parts) > 2 else ""
        else:
            # No quotes, take everything before flags
            desc_parts = []
            for p in params:
                if p.startswith('--'):
                    break
                desc_parts.append(p)
            desc = " ".join(desc_parts)
        
        if not desc:
            return "❌ Task description required. Use quotes: TASK ADD \"description\""
        
        # Parse flags
        if '--urgent' in full_text:
            is_urgent = True
        
        if '--due' in full_text:
            idx = params.index('--due') if '--due' in params else -1
            if idx >= 0 and idx + 1 < len(params):
                due_date = params[idx + 1]
        
        # Load tasks
        data = self._load_tasks()
        task_id = data['next_id']
        
        # Create task
        task = {
            'id': task_id,
            'description': desc,
            'status': 'pending',
            'priority': 'urgent' if is_urgent else 'normal',
            'due_date': due_date,
            'created': datetime.now().isoformat(),
            'completed': None,
            'progress': 0
        }
        
        data['tasks'].append(task)
        data['next_id'] += 1
        
        # Save
        if self._save_tasks(data):
            icon = "⚡" if is_urgent else "📋"
            due_info = f" (Due: {due_date})" if due_date else ""
            return f"✅ {icon} Task #{task_id} added: {desc}{due_info}"
        else:
            return "❌ Error saving task"
    
    def _task_done(self, params: List[str]) -> str:
        """Mark task as done."""
        if not params:
            return "❌ Usage: TASK DONE <id>"
        
        try:
            task_id = int(params[0])
        except ValueError:
            return f"❌ Invalid task ID: {params[0]}"
        
        data = self._load_tasks()
        task = next((t for t in data['tasks'] if t['id'] == task_id), None)
        
        if not task:
            return f"❌ Task #{task_id} not found"
        
        if task['status'] == 'done':
            return f"ℹ️  Task #{task_id} already marked as done"
        
        task['status'] = 'done'
        task['completed'] = datetime.now().isoformat()
        task['progress'] = 100
        
        if self._save_tasks(data):
            return f"✅ Task #{task_id} marked as done: {task['description']}"
        else:
            return "❌ Error saving task"
    
    def _task_delete(self, params: List[str]) -> str:
        """Delete a task."""
        if not params:
            return "❌ Usage: TASK DEL <id>"
        
        try:
            task_id = int(params[0])
        except ValueError:
            return f"❌ Invalid task ID: {params[0]}"
        
        data = self._load_tasks()
        task = next((t for t in data['tasks'] if t['id'] == task_id), None)
        
        if not task:
            return f"❌ Task #{task_id} not found"
        
        data['tasks'] = [t for t in data['tasks'] if t['id'] != task_id]
        
        if self._save_tasks(data):
            return f"🗑️  Task #{task_id} deleted: {task['description']}"
        else:
            return "❌ Error saving tasks"
    
    def _task_edit(self, params: List[str]) -> str:
        """
        Edit a task field.
        
        Note: Due to command parsing limitations, progress values may not parse correctly.
        Workaround: Use TASK DONE <id> to set progress to 100%, or edit tasks.json directly.
        """
        if len(params) < 3:
            return "❌ Usage: TASK EDIT <id> <field> <value>\n💡 Fields: description, priority, due_date, progress, status\n⚠️  Note: Some params may not parse correctly - use TASK DONE or edit tasks.json"
        
        try:
            task_id = int(params[0])
        except ValueError:
            return f"❌ Invalid task ID: {params[0]}"
        
        field = params[1].lower()
        value = " ".join(params[2:])
        
        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        
        data = self._load_tasks()
        task = next((t for t in data['tasks'] if t['id'] == task_id), None)
        
        if not task:
            return f"❌ Task #{task_id} not found"
        
        # Validate and update field
        if field == 'description':
            task['description'] = value
        elif field == 'priority':
            if value not in ['normal', 'urgent']:
                return "❌ Priority must be 'normal' or 'urgent'"
            task['priority'] = value
        elif field == 'due_date':
            task['due_date'] = value
        elif field == 'progress':
            try:
                progress = int(value)
                if not 0 <= progress <= 100:
                    return "❌ Progress must be 0-100"
                task['progress'] = progress
            except ValueError:
                return f"❌ Invalid progress value: {value}"
        elif field == 'status':
            if value not in ['pending', 'in_progress', 'done']:
                return "❌ Status must be 'pending', 'in_progress', or 'done'"
            task['status'] = value
            if value == 'done':
                task['completed'] = datetime.now().isoformat()
                task['progress'] = 100
        else:
            return f"❌ Unknown field: {field}\n💡 Fields: description, priority, due_date, progress, status"
        
        if self._save_tasks(data):
            return f"✅ Task #{task_id} updated: {field} = {value}"
        else:
            return "❌ Error saving task"


def handle_calendar_command(params, grid, parser):
    """
    Entry point for calendar commands.
    
    Args:
        params: Command parameters
        grid: Grid object
        parser: Parser object
        
    Returns:
        Formatted calendar output
    """
    from core.config import Config
    
    config = Config()
    handler = CalendarHandler(config)
    return handler.handle_command(params)
