"""
uDOS Progress Manager - Real-time progress indicators for long-running operations.

This module provides sophisticated progress tracking with animated indicators,
time estimates, cancellation support, and adaptive display formatting.

Author: uDOS Development Team
Version: 1.0.6
"""

import threading
import time
import sys
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class ProgressType(Enum):
    """Types of progress indicators."""
    DETERMINATE = "determinate"      # Known total (progress bar)
    INDETERMINATE = "indeterminate"  # Unknown total (spinner)
    MULTI_STAGE = "multi_stage"      # Multiple phases
    PARALLEL = "parallel"            # Multiple concurrent operations


@dataclass
class ProgressConfig:
    """Configuration for progress indicators."""
    show_percentage: bool = True
    show_time_estimate: bool = True
    show_elapsed_time: bool = True
    show_speed: bool = False
    show_cancel_hint: bool = True
    update_interval: float = 0.1
    width: int = 40
    style: str = "block"  # block, bar, dots, arrow


class ProgressIndicator:
    """Individual progress indicator with real-time updates."""

    def __init__(self, task_id: str, description: str, total: Optional[int] = None,
                 config: Optional[ProgressConfig] = None):
        self.task_id = task_id
        self.description = description
        self.total = total
        self.current = 0
        self.config = config or ProgressConfig()

        self.start_time = datetime.now()
        self.last_update = self.start_time
        self.speed_samples = []
        self.status = "running"
        self.cancelled = False
        self.error = None

        # Display state
        self.spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.spinner_index = 0

        # Threading
        self._update_thread = None
        self._stop_event = threading.Event()

    def start(self):
        """Start the progress indicator."""
        if self._update_thread is None or not self._update_thread.is_alive():
            self._stop_event.clear()
            self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self._update_thread.start()

    def stop(self):
        """Stop the progress indicator."""
        self._stop_event.set()
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join(timeout=1.0)

    def update(self, current: int, message: str = ""):
        """Update progress value."""
        self.current = current
        if message:
            self.description = message

        # Calculate speed
        now = datetime.now()
        if len(self.speed_samples) > 0:
            time_diff = (now - self.last_update).total_seconds()
            if time_diff > 0:
                speed = (current - (self.speed_samples[-1][1] if self.speed_samples else 0)) / time_diff
                self.speed_samples.append((now, current, speed))

                # Keep only recent samples
                if len(self.speed_samples) > 10:
                    self.speed_samples = self.speed_samples[-10:]
        else:
            self.speed_samples.append((now, current, 0))

        self.last_update = now

    def increment(self, amount: int = 1, message: str = ""):
        """Increment progress by amount."""
        self.update(self.current + amount, message)

    def complete(self, message: str = ""):
        """Mark progress as completed."""
        self.status = "completed"
        if self.total:
            self.current = self.total
        if message:
            self.description = message
        self.stop()

    def cancel(self, message: str = ""):
        """Cancel the operation."""
        self.status = "cancelled"
        self.cancelled = True
        if message:
            self.description = message
        self.stop()

    def error(self, error_message: str):
        """Mark as error."""
        self.status = "error"
        self.error = error_message
        self.stop()

    def _update_loop(self):
        """Background update loop for display."""
        while not self._stop_event.wait(self.config.update_interval):
            if self.status == "running":
                self._render()

    def _render(self):
        """Render the progress indicator."""
        # Move cursor to beginning of line and clear
        sys.stdout.write('\r\033[K')

        # Build progress display
        display = self._build_display()

        # Write to stdout
        sys.stdout.write(display)
        sys.stdout.flush()

        # Update spinner
        self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)

    def _build_display(self) -> str:
        """Build the progress display string."""
        parts = []

        # Status indicator
        if self.status == "running":
            if self.total is not None:
                # Determinate progress
                parts.append(self._build_progress_bar())
            else:
                # Indeterminate progress
                parts.append(f"{self.spinner_chars[self.spinner_index]} ")
        elif self.status == "completed":
            parts.append("✅ ")
        elif self.status == "cancelled":
            parts.append("🚫 ")
        elif self.status == "error":
            parts.append("❌ ")

        # Task description
        parts.append(f"{self.description}")

        # Progress information
        info_parts = []

        if self.total is not None and self.config.show_percentage:
            percentage = (self.current / self.total * 100) if self.total > 0 else 0
            info_parts.append(f"{percentage:.1f}%")

        if self.config.show_elapsed_time:
            elapsed = datetime.now() - self.start_time
            info_parts.append(f"⏱️{self._format_duration(elapsed)}")

        if self.config.show_time_estimate and self.total is not None and self.current > 0:
            eta = self._calculate_eta()
            if eta:
                info_parts.append(f"ETA {self._format_duration(eta)}")

        if self.config.show_speed and len(self.speed_samples) > 1:
            avg_speed = sum(sample[2] for sample in self.speed_samples[-5:]) / min(5, len(self.speed_samples))
            if avg_speed > 0:
                info_parts.append(f"{avg_speed:.1f}/s")

        if info_parts:
            parts.append(f" ({', '.join(info_parts)})")

        if self.config.show_cancel_hint and self.status == "running":
            parts.append(" [Ctrl+C to cancel]")

        return "".join(parts)

    def _build_progress_bar(self) -> str:
        """Build a visual progress bar."""
        if self.total is None or self.total == 0:
            return ""

        filled_width = int(self.config.width * self.current / self.total)

        if self.config.style == "block":
            filled = "█" * filled_width
            empty = "░" * (self.config.width - filled_width)
            return f"[{filled}{empty}] "
        elif self.config.style == "bar":
            filled = "=" * filled_width
            empty = "-" * (self.config.width - filled_width)
            pointer = ">" if filled_width < self.config.width else ""
            return f"[{filled}{pointer}{empty}] "
        elif self.config.style == "dots":
            filled = "●" * filled_width
            empty = "○" * (self.config.width - filled_width)
            return f"{filled}{empty} "
        else:  # arrow
            filled = "▶" * filled_width
            empty = "▷" * (self.config.width - filled_width)
            return f"{filled}{empty} "

    def _calculate_eta(self) -> Optional[timedelta]:
        """Calculate estimated time to completion."""
        if not self.speed_samples or self.current == 0 or self.total is None:
            return None

        # Use average speed from recent samples
        recent_samples = self.speed_samples[-5:]
        avg_speed = sum(sample[2] for sample in recent_samples) / len(recent_samples)

        if avg_speed <= 0:
            return None

        remaining = self.total - self.current
        eta_seconds = remaining / avg_speed
        return timedelta(seconds=eta_seconds)

    def _format_duration(self, duration: timedelta) -> str:
        """Format duration for display."""
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


class MultiStageProgress:
    """Progress indicator for multi-stage operations."""

    def __init__(self, task_id: str, stages: List[str], config: Optional[ProgressConfig] = None):
        self.task_id = task_id
        self.stages = stages
        self.config = config or ProgressConfig()

        self.current_stage = 0
        self.stage_progress = 0
        self.stage_total = 100

        self.start_time = datetime.now()
        self.status = "running"

        # Individual stage indicators
        self.current_indicator = None

    def start_stage(self, stage_index: int, description: str = "", total: Optional[int] = None):
        """Start a specific stage."""
        if 0 <= stage_index < len(self.stages):
            self.current_stage = stage_index
            self.stage_progress = 0
            self.stage_total = total or 100

            # Stop previous indicator
            if self.current_indicator:
                self.current_indicator.stop()

            # Create new indicator for this stage
            stage_desc = description or self.stages[stage_index]
            full_desc = f"Stage {stage_index + 1}/{len(self.stages)}: {stage_desc}"

            self.current_indicator = ProgressIndicator(
                f"{self.task_id}_stage_{stage_index}",
                full_desc,
                self.stage_total,
                self.config
            )
            self.current_indicator.start()

    def update_stage(self, progress: int, message: str = ""):
        """Update current stage progress."""
        if self.current_indicator:
            self.current_indicator.update(progress, message)
        self.stage_progress = progress

    def complete_stage(self, message: str = ""):
        """Complete current stage."""
        if self.current_indicator:
            self.current_indicator.complete(message)
        self.stage_progress = self.stage_total

    def complete(self, message: str = ""):
        """Complete all stages."""
        if self.current_indicator:
            self.current_indicator.complete(message)
        self.status = "completed"

    def get_overall_progress(self) -> float:
        """Get overall progress across all stages."""
        if not self.stages:
            return 100.0

        stage_weight = 100.0 / len(self.stages)
        completed_stages = self.current_stage * stage_weight
        current_stage_progress = (self.stage_progress / self.stage_total) * stage_weight

        return completed_stages + current_stage_progress


class ProgressManager:
    """Manager for multiple progress indicators."""

    def __init__(self):
        self.indicators: Dict[str, ProgressIndicator] = {}
        self.multi_stage_indicators: Dict[str, MultiStageProgress] = {}
        self._lock = threading.Lock()

    def create_progress(self, task_id: str, description: str, total: Optional[int] = None,
                       config: Optional[ProgressConfig] = None) -> ProgressIndicator:
        """Create a new progress indicator."""
        with self._lock:
            indicator = ProgressIndicator(task_id, description, total, config)
            self.indicators[task_id] = indicator
            return indicator

    def create_multi_stage_progress(self, task_id: str, stages: List[str],
                                   config: Optional[ProgressConfig] = None) -> MultiStageProgress:
        """Create a multi-stage progress indicator."""
        with self._lock:
            indicator = MultiStageProgress(task_id, stages, config)
            self.multi_stage_indicators[task_id] = indicator
            return indicator

    def get_progress(self, task_id: str) -> Optional[ProgressIndicator]:
        """Get an existing progress indicator."""
        return self.indicators.get(task_id)

    def get_multi_stage_progress(self, task_id: str) -> Optional[MultiStageProgress]:
        """Get an existing multi-stage progress indicator."""
        return self.multi_stage_indicators.get(task_id)

    def remove_progress(self, task_id: str):
        """Remove a progress indicator."""
        with self._lock:
            if task_id in self.indicators:
                self.indicators[task_id].stop()
                del self.indicators[task_id]

            if task_id in self.multi_stage_indicators:
                indicator = self.multi_stage_indicators[task_id]
                if indicator.current_indicator:
                    indicator.current_indicator.stop()
                del self.multi_stage_indicators[task_id]

    def cleanup_completed(self):
        """Remove all completed indicators."""
        with self._lock:
            completed_ids = [
                task_id for task_id, indicator in self.indicators.items()
                if indicator.status in ["completed", "cancelled", "error"]
            ]

            for task_id in completed_ids:
                self.remove_progress(task_id)

    def cancel_all(self):
        """Cancel all running progress indicators."""
        with self._lock:
            for indicator in self.indicators.values():
                if indicator.status == "running":
                    indicator.cancel("Operation cancelled by user")

            for indicator in self.multi_stage_indicators.values():
                if indicator.status == "running":
                    if indicator.current_indicator:
                        indicator.current_indicator.cancel("Operation cancelled by user")

    def get_active_count(self) -> int:
        """Get count of active progress indicators."""
        active_count = sum(
            1 for indicator in self.indicators.values()
            if indicator.status == "running"
        )

        active_count += sum(
            1 for indicator in self.multi_stage_indicators.values()
            if indicator.status == "running"
        )

        return active_count


# Global progress manager instance
progress_manager = ProgressManager()


def with_progress(task_id: str, description: str, total: Optional[int] = None,
                 config: Optional[ProgressConfig] = None):
    """Decorator for adding progress indicators to functions."""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            indicator = progress_manager.create_progress(task_id, description, total, config)
            indicator.start()

            try:
                # Pass indicator to function if it accepts it
                import inspect
                sig = inspect.signature(func)
                if 'progress_indicator' in sig.parameters:
                    kwargs['progress_indicator'] = indicator

                result = func(*args, **kwargs)
                indicator.complete("Operation completed successfully")
                return result

            except KeyboardInterrupt:
                indicator.cancel("Operation cancelled by user")
                raise
            except Exception as e:
                indicator.error(f"Operation failed: {str(e)}")
                raise
            finally:
                progress_manager.remove_progress(task_id)

        return wrapper
    return decorator


def with_multi_stage_progress(task_id: str, stages: List[str],
                             config: Optional[ProgressConfig] = None):
    """Decorator for adding multi-stage progress indicators to functions."""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            indicator = progress_manager.create_multi_stage_progress(task_id, stages, config)

            try:
                # Pass indicator to function if it accepts it
                import inspect
                sig = inspect.signature(func)
                if 'multi_stage_progress' in sig.parameters:
                    kwargs['multi_stage_progress'] = indicator

                result = func(*args, **kwargs)
                indicator.complete("All stages completed successfully")
                return result

            except KeyboardInterrupt:
                if indicator.current_indicator:
                    indicator.current_indicator.cancel("Operation cancelled by user")
                raise
            except Exception as e:
                if indicator.current_indicator:
                    indicator.current_indicator.error(f"Operation failed: {str(e)}")
                raise
            finally:
                progress_manager.remove_progress(task_id)

        return wrapper
    return decorator
