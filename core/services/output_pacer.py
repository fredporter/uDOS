"""
Output Pacer for uDOS Mission Control

Provides organic, viewport-aware output pacing for mission execution:
- Character-by-character typing with configurable speed
- Speed ramping (slow → fast → slow) for natural feel
- Viewport awareness and fullness calculation
- Breathing pauses between sections
- Progress animations (spinners, bars, dots)
- User pause detection when viewport is full
- Section detection for intelligent breaks

Author: uDOS Development Team
Version: 1.1.2
"""

import os
import shutil
import sys
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class AnimationType(Enum):
    """Types of progress animations."""
    SPINNER = "spinner"
    DOTS = "dots"
    BAR = "bar"
    PERCENTAGE = "percentage"


class ContentType(Enum):
    """Types of content for pacing decisions."""
    TEXT = "text"
    CODE = "code"
    DATA = "data"
    HEADER = "header"
    LIST = "list"


class OutputPacer:
    """
    Manages organic output pacing for mission execution.

    Features:
    - Typewriter effect with configurable speed
    - Speed ramping for natural feel
    - Viewport awareness (terminal size detection)
    - Fullness calculation (% of viewport used)
    - Breathing pauses between sections
    - Section detection (headers, paragraphs, code blocks)
    - Progress animations (spinners, bars, dots)
    - User pause detection when viewport full

    Example:
        >>> pacer = OutputPacer(chars_per_second=50)
        >>> pacer.type_text("Processing mission...", speed_ramp=True)
        >>> pacer.breathing_pause()
        >>>
        >>> with pacer.progress_animation('spinner', "Loading"):
        ...     # Long operation
        ...     process_data()
    """

    def __init__(
        self,
        chars_per_second: int = 40,
        enable_typing: bool = True,
        enable_pauses: bool = True,
        enable_animations: bool = True,
        viewport_threshold: float = 0.8
    ):
        """
        Initialize OutputPacer.

        Args:
            chars_per_second: Base typing speed (default: 40)
            enable_typing: Enable typewriter effect (default: True)
            enable_pauses: Enable breathing pauses (default: True)
            enable_animations: Enable progress animations (default: True)
            viewport_threshold: Pause when viewport is this full (default: 0.8 = 80%)
        """
        self.chars_per_second = chars_per_second
        self.enable_typing = enable_typing
        self.enable_pauses = enable_pauses
        self.enable_animations = enable_animations
        self.viewport_threshold = viewport_threshold

        # Viewport tracking
        self.lines_printed = 0
        self.viewport_height = self._get_viewport_height()

        # Speed ramping configuration
        self.ramp_start_speed = 0.5  # Start at 50% of base speed
        self.ramp_end_speed = 0.5    # End at 50% of base speed
        self.ramp_peak_speed = 1.5   # Peak at 150% of base speed

        # Pause durations (milliseconds)
        self.pause_short = 200   # Between sentences
        self.pause_medium = 350  # Between paragraphs
        self.pause_long = 500    # Between sections

        # Animation characters
        self.spinner_frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.dots_max = 3

        # Section markers
        self.header_markers = ['#', '=', '-', '✅', '❌', '⚠️', '🔥', '📊']
        self.code_markers = ['```', '    ', '\t']

    def _get_viewport_height(self) -> int:
        """Get terminal viewport height."""
        try:
            size = shutil.get_terminal_size(fallback=(80, 24))
            return size.lines
        except Exception:
            return 24  # Fallback

    def _get_viewport_width(self) -> int:
        """Get terminal viewport width."""
        try:
            size = shutil.get_terminal_size(fallback=(80, 24))
            return size.columns
        except Exception:
            return 80  # Fallback

    def get_viewport_fullness(self) -> float:
        """
        Calculate viewport fullness (0.0 to 1.0).

        Returns:
            Float representing percentage of viewport used
        """
        if self.viewport_height == 0:
            return 0.0

        fullness = self.lines_printed / self.viewport_height
        return min(1.0, fullness)  # Cap at 100%

    def is_viewport_full(self) -> bool:
        """Check if viewport has exceeded threshold."""
        return self.get_viewport_fullness() >= self.viewport_threshold

    def reset_viewport_tracking(self) -> None:
        """Reset line counter (e.g., after screen clear)."""
        self.lines_printed = 0

    def wait_for_user(self, message: str = "Press ENTER to continue...") -> None:
        """
        Wait for user input before continuing.

        Args:
            message: Prompt to display
        """
        try:
            input(f"\n{message} ")
            self.reset_viewport_tracking()
        except KeyboardInterrupt:
            print("\n")
            raise

    def detect_content_type(self, text: str) -> ContentType:
        """
        Detect content type for pacing decisions.

        Args:
            text: Text to analyze

        Returns:
            ContentType enum value
        """
        stripped = text.lstrip()

        # Check for lists FIRST (before headers, since '-' can be both)
        if stripped.startswith(('- ', '* ', '+ ', '• ')) or \
           (len(stripped) > 0 and stripped[0].isdigit() and '. ' in stripped[:5]):
            return ContentType.LIST

        # Check for code
        if any(marker in text for marker in self.code_markers):
            return ContentType.CODE

        # Check for headers (excluding single '-' which is list)
        for marker in self.header_markers:
            if marker in ['-', '=']:
                # For - and =, need multiple in a row or at start of line followed by space
                if stripped.startswith(marker * 3) or stripped.startswith(marker + ' '):
                    return ContentType.HEADER
            elif stripped.startswith(marker):
                return ContentType.HEADER

        # Check for data (JSON-like, key-value pairs)
        # Must have both ':' and either '{' or '='
        if ':' in text and '{' in text:
            return ContentType.DATA

        if '=' in text and not ' ' in text.split('=')[0].strip()[-5:]:
            # Has = and left side looks like a variable name (no spaces near end)
            return ContentType.DATA

        return ContentType.TEXT
    
    def calculate_speed_multiplier(
        self,
        position: int,
        total_length: int,
        enable_ramp: bool = True
    ) -> float:
        """
        Calculate speed multiplier with ramping (slow → fast → slow).

        Args:
            position: Current character position
            total_length: Total text length
            enable_ramp: Enable speed ramping

        Returns:
            Speed multiplier (e.g., 0.5 = 50% speed, 1.5 = 150% speed)
        """
        if not enable_ramp or total_length == 0:
            return 1.0

        # Calculate position ratio (0.0 to 1.0)
        ratio = position / total_length

        # Use a smooth curve: slow start → fast middle → slow end
        # Quadratic easing in/out
        if ratio < 0.5:
            # First half: ramp up from start speed to peak speed
            progress = ratio * 2  # 0.0 to 1.0
            multiplier = self.ramp_start_speed + \
                        (self.ramp_peak_speed - self.ramp_start_speed) * progress
        else:
            # Second half: ramp down from peak speed to end speed
            progress = (ratio - 0.5) * 2  # 0.0 to 1.0
            multiplier = self.ramp_peak_speed - \
                        (self.ramp_peak_speed - self.ramp_end_speed) * progress

        return multiplier

    def type_text(
        self,
        text: str,
        speed_ramp: bool = True,
        newline: bool = True,
        flush: bool = True
    ) -> None:
        """
        Display text with typewriter effect.

        Args:
            text: Text to display
            speed_ramp: Enable speed ramping (default: True)
            newline: Add newline at end (default: True)
            flush: Flush after each character (default: True)
        """
        if not self.enable_typing or not text:
            # Fast path: no typing effect
            print(text, end='\n' if newline else '', flush=flush)
            self.lines_printed += text.count('\n') + (1 if newline else 0)
            return

        # Typing effect
        total_length = len(text)

        for i, char in enumerate(text):
            # Calculate delay with speed ramping
            multiplier = self.calculate_speed_multiplier(i, total_length, speed_ramp)
            delay = (1.0 / self.chars_per_second) / multiplier

            # Print character
            print(char, end='', flush=flush)

            # Track newlines
            if char == '\n':
                self.lines_printed += 1

            # Delay (except for last character)
            if i < total_length - 1:
                time.sleep(delay)

        # Add final newline if requested
        if newline:
            print(flush=flush)
            self.lines_printed += 1

        # Check if viewport is full and pause if needed
        if self.is_viewport_full():
            self.wait_for_user()

    def breathing_pause(self, duration: Optional[int] = None) -> None:
        """
        Add a breathing pause for readability.

        Args:
            duration: Pause duration in milliseconds (default: medium pause)
        """
        if not self.enable_pauses:
            return

        if duration is None:
            duration = self.pause_medium

        time.sleep(duration / 1000.0)

    def section_break(self, pause: bool = True) -> None:
        """
        Add a section break (visual + pause).

        Args:
            pause: Add breathing pause (default: True)
        """
        print()  # Blank line
        self.lines_printed += 1

        if pause:
            self.breathing_pause(self.pause_long)

    def detect_sections(self, text: str) -> List[Tuple[int, int, ContentType]]:
        """
        Detect sections in text for intelligent breaks.

        Args:
            text: Text to analyze

        Returns:
            List of (start_index, end_index, content_type) tuples
        """
        sections = []
        lines = text.split('\n')

        current_start = 0
        current_type = None

        for i, line in enumerate(lines):
            line_type = self.detect_content_type(line)

            if line_type != current_type:
                # Section boundary
                if current_type is not None:
                    # End previous section
                    sections.append((current_start, i - 1, current_type))

                # Start new section
                current_start = i
                current_type = line_type

        # Add final section
        if current_type is not None:
            sections.append((current_start, len(lines) - 1, current_type))

        return sections

    def type_with_sections(
        self,
        text: str,
        pause_between_sections: bool = True
    ) -> None:
        """
        Type text with intelligent section detection and pausing.

        Args:
            text: Text to display
            pause_between_sections: Add pauses between sections (default: True)
        """
        lines = text.split('\n')
        sections = self.detect_sections(text)

        for i, (start, end, content_type) in enumerate(sections):
            section_text = '\n'.join(lines[start:end + 1])

            # Type section
            self.type_text(section_text, speed_ramp=True, newline=True)

            # Pause between sections (except after last section)
            if pause_between_sections and i < len(sections) - 1:
                # Longer pause for major transitions
                if content_type == ContentType.HEADER:
                    self.breathing_pause(self.pause_long)
                elif content_type == ContentType.CODE:
                    self.breathing_pause(self.pause_medium)
                else:
                    self.breathing_pause(self.pause_short)

    def progress_spinner(
        self,
        message: str,
        duration: float = 0.0,
        update_callback: Optional[Callable[[], bool]] = None
    ) -> None:
        """
        Display a progress spinner.

        Args:
            message: Message to display
            duration: Run for fixed duration (0 = manual control via callback)
            update_callback: Function that returns True to continue, False to stop
        """
        if not self.enable_animations:
            print(message)
            return

        start_time = time.time()
        frame_index = 0

        try:
            while True:
                # Check stop conditions
                if duration > 0 and time.time() - start_time >= duration:
                    break

                if update_callback and not update_callback():
                    break

                # Display frame
                frame = self.spinner_frames[frame_index % len(self.spinner_frames)]
                print(f'\r{frame} {message}', end='', flush=True)

                frame_index += 1
                time.sleep(0.1)
        finally:
            print('\r' + ' ' * (len(message) + 3) + '\r', end='', flush=True)

    def progress_dots(
        self,
        message: str,
        duration: float = 0.0,
        update_callback: Optional[Callable[[], bool]] = None
    ) -> None:
        """
        Display animated dots (...).

        Args:
            message: Message to display
            duration: Run for fixed duration (0 = manual control via callback)
            update_callback: Function that returns True to continue, False to stop
        """
        if not self.enable_animations:
            print(message)
            return

        start_time = time.time()
        dot_count = 0

        try:
            while True:
                # Check stop conditions
                if duration > 0 and time.time() - start_time >= duration:
                    break

                if update_callback and not update_callback():
                    break

                # Display dots
                dots = '.' * ((dot_count % self.dots_max) + 1)
                padding = ' ' * (self.dots_max - len(dots))
                print(f'\r{message}{dots}{padding}', end='', flush=True)

                dot_count += 1
                time.sleep(0.5)
        finally:
            print('\r' + ' ' * (len(message) + self.dots_max + 1) + '\r', end='', flush=True)

    def progress_bar(
        self,
        current: int,
        total: int,
        message: str = "",
        width: int = 40
    ) -> None:
        """
        Display a progress bar.

        Args:
            current: Current progress value
            total: Total value (100%)
            message: Optional message to display
            width: Bar width in characters (default: 40)
        """
        if not self.enable_animations or total == 0:
            return

        percent = min(100, int((current / total) * 100))
        filled = int((current / total) * width)
        bar = '█' * filled + '░' * (width - filled)

        print(f'\r{message} [{bar}] {percent}%', end='', flush=True)

        if current >= total:
            print()  # Newline when complete
            self.lines_printed += 1

    def animate_with_type(
        self,
        animation_type: AnimationType,
        message: str,
        duration: float = 2.0
    ) -> None:
        """
        Display an animation with a message.

        Args:
            animation_type: Type of animation
            message: Message to display
            duration: Animation duration in seconds
        """
        if animation_type == AnimationType.SPINNER:
            self.progress_spinner(message, duration=duration)
        elif animation_type == AnimationType.DOTS:
            self.progress_dots(message, duration=duration)
        else:
            # Fallback: just type the message
            self.type_text(message)

    def get_pacing_config(self) -> Dict[str, Any]:
        """Get current pacing configuration."""
        return {
            'chars_per_second': self.chars_per_second,
            'enable_typing': self.enable_typing,
            'enable_pauses': self.enable_pauses,
            'enable_animations': self.enable_animations,
            'viewport_threshold': self.viewport_threshold,
            'viewport_height': self.viewport_height,
            'lines_printed': self.lines_printed,
            'fullness': self.get_viewport_fullness()
        }

    def update_config(
        self,
        chars_per_second: Optional[int] = None,
        enable_typing: Optional[bool] = None,
        enable_pauses: Optional[bool] = None,
        enable_animations: Optional[bool] = None,
        viewport_threshold: Optional[float] = None
    ) -> None:
        """
        Update pacing configuration.

        Args:
            chars_per_second: New typing speed
            enable_typing: Enable/disable typing effect
            enable_pauses: Enable/disable breathing pauses
            enable_animations: Enable/disable progress animations
            viewport_threshold: New viewport threshold
        """
        if chars_per_second is not None:
            self.chars_per_second = max(1, chars_per_second)

        if enable_typing is not None:
            self.enable_typing = enable_typing

        if enable_pauses is not None:
            self.enable_pauses = enable_pauses

        if enable_animations is not None:
            self.enable_animations = enable_animations

        if viewport_threshold is not None:
            self.viewport_threshold = max(0.0, min(1.0, viewport_threshold))


# Singleton instance
_output_pacer: Optional[OutputPacer] = None


def get_output_pacer() -> OutputPacer:
    """Get singleton OutputPacer instance."""
    global _output_pacer
    if _output_pacer is None:
        _output_pacer = OutputPacer()
    return _output_pacer
