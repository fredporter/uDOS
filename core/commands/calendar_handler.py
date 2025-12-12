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
        
    def handle_command(self, params):
        """
        Handle CAL/CALENDAR commands.
        
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
        
        else:
            return f"❌ Unknown CAL command: {subcommand}\n💡 Use: CAL [MONTH|WEEK|DAY|NEXT|PREV]"
    
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
