"""
Time Command Handler

Handles all time-related commands: CLOCK, TIMER, EGG, STOPWATCH, CALENDAR

Part of v1.2.22 - Self-Healing & Auto-Error-Awareness System
"""

import os
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import List, Optional
from calendar import monthcalendar, month_name, day_name

from .base_handler import BaseCommandHandler
from core.services.timedate_manager import get_timedate_manager


class TimeHandler(BaseCommandHandler):
    """Handler for time-related commands."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timedate_manager = get_timedate_manager()
        
        # Timer state
        self.active_timer = None
        self.timer_thread = None
        
        # Stopwatch state
        self.stopwatch_start = None
        self.stopwatch_laps = []
        self.stopwatch_running = False
    
    def handle(self, command: str, params: List[str], grid=None) -> str:
        """
        Handle TIME commands.
        
        Args:
            command: Command name
            params: Command parameters
            grid: Optional grid instance
            
        Returns:
            Command result
        """
        cmd = command.upper()
        
        if cmd == 'CLOCK':
            return self._handle_clock(params)
        elif cmd == 'TIMER':
            return self._handle_timer(params)
        elif cmd == 'EGG':
            return self._handle_egg(params)
        elif cmd == 'STOPWATCH':
            return self._handle_stopwatch(params)
        elif cmd == 'CALENDAR':
            return self._handle_calendar(params)
        elif cmd == 'TIME':
            # General TIME command - show current time
            return self._handle_time(params)
        else:
            return f"Unknown time command: {cmd}"
    
    def _handle_time(self, params: List[str]) -> str:
        """Handle TIME command - show current time."""
        if not params:
            # Show current time in current timezone
            tz_info = self.timedate_manager.get_time_info()
            time_str = self.timedate_manager.get_current_time()
            
            output = [f"\n🕐 Current Time"]
            output.append(f"   {time_str}")
            output.append(f"   {tz_info.name} ({tz_info.abbreviation} {tz_info.offset})")
            
            if tz_info.city:
                output.append(f"   📍 {tz_info.city}")
            
            if tz_info.tile:
                output.append(f"   🗺️  TILE {tz_info.tile}")
            
            return "\n".join(output)
        
        subcommand = params[0].upper()
        
        if subcommand == 'SET':
            # Set timezone
            if len(params) < 2:
                return "Usage: TIME SET <timezone|city>"
            
            tz_name = ' '.join(params[1:])
            if self.timedate_manager.set_timezone(tz_name):
                tz_info = self.timedate_manager.get_time_info()
                return f"✅ Timezone set to: {tz_info.name} ({tz_info.abbreviation})"
            else:
                return f"❌ Unknown timezone or city: {tz_name}"
        
        elif subcommand == 'ADD':
            # Add tracked timezone
            if len(params) < 2:
                return "Usage: TIME ADD <timezone|city>"
            
            tz_name = ' '.join(params[1:])
            if self.timedate_manager.add_tracked_zone(tz_name):
                return f"✅ Added to tracked zones: {tz_name}"
            else:
                return f"❌ Failed to add timezone: {tz_name}"
        
        elif subcommand == 'REMOVE':
            # Remove tracked timezone
            if len(params) < 2:
                return "Usage: TIME REMOVE <timezone>"
            
            tz_name = ' '.join(params[1:])
            if self.timedate_manager.remove_tracked_zone(tz_name):
                return f"✅ Removed from tracked zones: {tz_name}"
            else:
                return f"❌ Timezone not in tracked list: {tz_name}"
        
        elif subcommand == 'LIST':
            # List tracked timezones
            times = self.timedate_manager.get_multiple_times()
            
            if not times:
                return "No tracked timezones"
            
            output = ["\n🌍 Tracked Timezones"]
            output.append("=" * 60)
            
            for tz_info, time_str in times:
                output.append(f"{time_str}  {tz_info.name} ({tz_info.abbreviation})")
                if tz_info.city:
                    output.append(f"         📍 {tz_info.city}")
            
            return "\n".join(output)
        
        else:
            return f"Unknown TIME subcommand: {subcommand}\nUse: TIME SET|ADD|REMOVE|LIST"
    
    def _handle_clock(self, params: List[str]) -> str:
        """Handle CLOCK command - ASCII 7-segment display."""
        # Get time to display
        if params and params[0].upper() != 'MULTI':
            # Specific timezone
            tz_name = ' '.join(params)
            time_str = self.timedate_manager.get_current_time(tz_name, "%H:%M:%S")
            tz_info = self.timedate_manager.get_time_info(tz_name)
        else:
            # Current timezone
            time_str = self.timedate_manager.get_current_time(None, "%H:%M:%S")
            tz_info = self.timedate_manager.get_time_info()
        
        # ASCII 7-segment display
        clock_display = self._render_7segment(time_str)
        
        output = ["\n" + clock_display]
        output.append(f"\n{tz_info.name} ({tz_info.abbreviation} {tz_info.offset})")
        
        if params and params[0].upper() == 'MULTI':
            # Show multiple timezones
            output.append("\n🌍 Other Timezones:")
            times = self.timedate_manager.get_multiple_times()
            for tz_info, time_str in times:
                output.append(f"  {time_str}  {tz_info.abbreviation}")
        
        return "\n".join(output)
    
    def _render_7segment(self, time_str: str) -> str:
        """Render time in ASCII 7-segment display."""
        # 7-segment digit patterns (5 lines tall, 3 chars wide)
        digits = {
            '0': [' ▄▄▄ ', '█   █', '█   █', '█   █', ' ▀▀▀ '],
            '1': ['  █  ', ' ██  ', '  █  ', '  █  ', ' ███ '],
            '2': [' ▄▄▄ ', '    █', ' ▄▄▄ ', '█    ', ' ▀▀▀▀'],
            '3': [' ▄▄▄ ', '    █', '  ▄▄ ', '    █', ' ▀▀▀ '],
            '4': ['█   █', '█   █', ' ▀▀▀█', '    █', '    █'],
            '5': [' ▄▄▄▄', '█    ', ' ▀▀▀ ', '    █', ' ▀▀▀ '],
            '6': [' ▄▄▄ ', '█    ', '█▄▄▄ ', '█   █', ' ▀▀▀ '],
            '7': [' ▀▀▀▀', '    █', '   █ ', '  █  ', ' █   '],
            '8': [' ▄▄▄ ', '█   █', ' ▄▄▄ ', '█   █', ' ▀▀▀ '],
            '9': [' ▄▄▄ ', '█   █', ' ▀▀▀█', '    █', ' ▀▀▀ '],
            ':': ['     ', '  •  ', '     ', '  •  ', '     ']
        }
        
        # Build display line by line
        lines = ['', '', '', '', '']
        for char in time_str:
            if char in digits:
                digit_lines = digits[char]
                for i in range(5):
                    lines[i] += digit_lines[i] + ' '
        
        return '\n'.join(lines)
    
    def _handle_timer(self, params: List[str]) -> str:
        """Handle TIMER command - countdown timer."""
        if not params:
            return ("Usage: TIMER <duration>\n"
                   "Examples:\n"
                   "  TIMER 5m          - 5 minute timer\n"
                   "  TIMER 1h 30m      - 1 hour 30 minutes\n"
                   "  TIMER 2:30:00     - 2 hours 30 minutes (HH:MM:SS)\n"
                   "  TIMER STOP        - Stop active timer\n"
                   "  TIMER STATUS      - Check timer status")
        
        subcommand = params[0].upper()
        
        if subcommand == 'STOP':
            if self.active_timer:
                self.active_timer = None
                return "⏹️  Timer stopped"
            else:
                return "No active timer"
        
        elif subcommand == 'STATUS':
            if self.active_timer:
                remaining = self.active_timer - time.time()
                if remaining > 0:
                    duration_str = self.timedate_manager.format_duration(int(remaining))
                    return f"⏱️  Timer active: {duration_str} remaining"
                else:
                    self.active_timer = None
                    return "⏰ Timer expired!"
            else:
                return "No active timer"
        
        else:
            # Start timer
            duration_str = ' '.join(params)
            seconds = self.timedate_manager.parse_duration(duration_str)
            
            if not seconds:
                return f"❌ Invalid duration: {duration_str}"
            
            # Start timer
            self.active_timer = time.time() + seconds
            duration_display = self.timedate_manager.format_duration(seconds)
            
            return (f"⏱️  Timer started: {duration_display}\n"
                   f"Use: TIMER STATUS to check\n"
                   f"Use: TIMER STOP to cancel")
    
    def _handle_egg(self, params: List[str]) -> str:
        """Handle EGG command - intelligent egg timer with context."""
        if not params:
            return ("🥚 Egg Timer\n\n"
                   "Usage: EGG <type>\n\n"
                   "Types:\n"
                   "  soft      - 4 minutes (runny yolk)\n"
                   "  medium    - 7 minutes (creamy yolk)\n"
                   "  hard      - 10 minutes (solid yolk)\n"
                   "  jammy     - 6 minutes (slightly runny center)\n\n"
                   "Example: EGG soft")
        
        egg_type = params[0].lower()
        
        # Egg cooking times and descriptions
        egg_times = {
            'soft': (240, "Soft-boiled (runny yolk)", "Perfect for dipping toast!"),
            'medium': (420, "Medium-boiled (creamy yolk)", "Great for salads"),
            'hard': (600, "Hard-boiled (solid yolk)", "Ideal for snacks"),
            'jammy': (360, "Jammy egg (slightly runny center)", "Ramen-ready!")
        }
        
        if egg_type not in egg_times:
            return f"❌ Unknown egg type: {egg_type}\nUse: EGG soft|medium|hard|jammy"
        
        seconds, description, tip = egg_times[egg_type]
        
        # Start timer
        self.active_timer = time.time() + seconds
        duration_display = self.timedate_manager.format_duration(seconds)
        
        return (f"🥚 {description}\n"
               f"⏱️  Timer: {duration_display}\n"
               f"💡 {tip}\n\n"
               f"Use: TIMER STATUS to check")
    
    def _handle_stopwatch(self, params: List[str]) -> str:
        """Handle STOPWATCH command - lap timer."""
        if not params:
            return ("Usage: STOPWATCH <start|stop|lap|reset>\n\n"
                   "Commands:\n"
                   "  start  - Start/resume stopwatch\n"
                   "  stop   - Stop stopwatch\n"
                   "  lap    - Record lap time\n"
                   "  reset  - Reset stopwatch")
        
        subcommand = params[0].upper()
        
        if subcommand == 'START':
            if not self.stopwatch_running:
                if self.stopwatch_start is None:
                    self.stopwatch_start = time.time()
                    self.stopwatch_laps = []
                else:
                    # Resume
                    pass
                self.stopwatch_running = True
                return "⏱️  Stopwatch started"
            else:
                return "⏱️  Stopwatch already running"
        
        elif subcommand == 'STOP':
            if self.stopwatch_running:
                self.stopwatch_running = False
                elapsed = time.time() - self.stopwatch_start
                duration_str = self.timedate_manager.format_duration(int(elapsed))
                return f"⏹️  Stopwatch stopped: {duration_str}"
            else:
                return "Stopwatch not running"
        
        elif subcommand == 'LAP':
            if self.stopwatch_running:
                elapsed = time.time() - self.stopwatch_start
                self.stopwatch_laps.append(elapsed)
                lap_num = len(self.stopwatch_laps)
                lap_time = self.timedate_manager.format_duration(int(elapsed))
                return f"🏁 Lap {lap_num}: {lap_time}"
            else:
                return "❌ Stopwatch not running"
        
        elif subcommand == 'RESET':
            self.stopwatch_start = None
            self.stopwatch_laps = []
            self.stopwatch_running = False
            return "✅ Stopwatch reset"
        
        else:
            # Show status
            if self.stopwatch_start:
                elapsed = time.time() - self.stopwatch_start
                duration_str = self.timedate_manager.format_duration(int(elapsed))
                
                output = [f"\n⏱️  Stopwatch: {duration_str}"]
                output.append(f"Status: {'Running' if self.stopwatch_running else 'Stopped'}")
                
                if self.stopwatch_laps:
                    output.append(f"\n🏁 Laps ({len(self.stopwatch_laps)}):")
                    for i, lap_time in enumerate(self.stopwatch_laps, 1):
                        lap_str = self.timedate_manager.format_duration(int(lap_time))
                        output.append(f"  {i}. {lap_str}")
                
                return "\n".join(output)
            else:
                return "Stopwatch not started"
    
    def _handle_calendar(self, params: List[str]) -> str:
        """Handle CALENDAR command - month/year view."""
        # Parse parameters
        if params:
            try:
                if len(params) == 1:
                    # Year only
                    year = int(params[0])
                    month = datetime.now().month
                elif len(params) >= 2:
                    # Month and year
                    month = int(params[0])
                    year = int(params[1])
                else:
                    month = datetime.now().month
                    year = datetime.now().year
            except ValueError:
                return "❌ Invalid date format\nUsage: CALENDAR [month] [year]"
        else:
            # Current month
            now = datetime.now()
            month = now.month
            year = now.year
        
        # Validate month
        if month < 1 or month > 12:
            return f"❌ Invalid month: {month} (must be 1-12)"
        
        # Generate calendar
        cal = monthcalendar(year, month)
        month_str = month_name[month]
        
        # Build output
        output = [f"\n╔═══════════════════════════════════════╗"]
        output.append(f"║  {month_str} {year}".ljust(40) + "║")
        output.append(f"╠═══════════════════════════════════════╣")
        
        # Day headers
        day_headers = "  " + "  ".join([d[:2] for d in day_name])
        output.append(f"║ {day_headers}  ║")
        output.append(f"╠═══════════════════════════════════════╣")
        
        # Calendar weeks
        today = datetime.now()
        for week in cal:
            week_str = ""
            for day in week:
                if day == 0:
                    week_str += "   "
                else:
                    # Highlight today
                    if year == today.year and month == today.month and day == today.day:
                        week_str += f"[{day:2d}]"[:-1] if day < 10 else f"[{day}]"
                    else:
                        week_str += f" {day:2d}"
            output.append(f"║ {week_str}  ║")
        
        output.append(f"╚═══════════════════════════════════════╝")
        
        # Add timezone info
        tz_info = self.timedate_manager.get_time_info()
        time_str = self.timedate_manager.get_current_time(None, "%H:%M:%S")
        output.append(f"\n🕐 {time_str} {tz_info.abbreviation}")
        
        return "\n".join(output)


# Factory function
def create_time_handler(**kwargs):
    """Create TimeHandler instance."""
    return TimeHandler(**kwargs)
