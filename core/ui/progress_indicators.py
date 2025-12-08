"""
Progress Indicators - v1.0.23 Phase 8
Visual feedback for long operations

Features:
- Progress bars with percentage
- Spinners for indeterminate operations
- ETA calculation
- Multi-stage progress tracking

Author: uDOS Development Team
Version: 1.0.23
"""

import time
from typing import Optional, List
from datetime import datetime, timedelta
import sys


class ProgressBar:
    """Progress bar with percentage and ETA"""

    def __init__(self, total: int, width: int = 50, title: str = "Progress"):
        """
        Initialize progress bar

        Args:
            total: Total number of items
            width: Width of progress bar in characters
            title: Title to display
        """
        self.total = total
        self.width = width
        self.title = title
        self.current = 0
        self.start_time = time.time()

    def update(self, current: Optional[int] = None, increment: int = 1):
        """
        Update progress

        Args:
            current: Set to specific value, or None to increment
            increment: Amount to increment if current is None
        """
        if current is not None:
            self.current = current
        else:
            self.current += increment

        self.render()

    def render(self) -> str:
        """Render progress bar"""
        percentage = min(100, int((self.current / self.total) * 100)) if self.total > 0 else 0
        filled = int((self.current / self.total) * self.width) if self.total > 0 else 0

        # Calculate ETA
        elapsed = time.time() - self.start_time
        if self.current > 0:
            rate = self.current / elapsed
            remaining = (self.total - self.current) / rate if rate > 0 else 0
            eta_str = self._format_time(remaining)
        else:
            eta_str = "calculating..."

        # Build progress bar
        bar = "█" * filled + "░" * (self.width - filled)

        output = f"\r{self.title}: [{bar}] {percentage}% ({self.current}/{self.total}) ETA: {eta_str}"

        # Print without newline
        sys.stdout.write(output)
        sys.stdout.flush()

        # Newline when complete
        if self.current >= self.total:
            sys.stdout.write("\n")
            sys.stdout.flush()

        return output

    def _format_time(self, seconds: float) -> str:
        """Format seconds as human-readable time"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            mins = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s"
        else:
            hours = int(seconds / 3600)
            mins = int((seconds % 3600) / 60)
            return f"{hours}h {mins}m"

    def finish(self):
        """Mark progress as complete"""
        self.current = self.total
        self.render()


class Spinner:
    """Spinner for indeterminate operations"""

    SPINNERS = {
        'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        'line': ['|', '/', '-', '\\'],
        'arrow': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
        'blocks': ['▖', '▘', '▝', '▗'],
        'simple': ['.', 'o', 'O', '°', 'O', 'o'],
    }

    def __init__(self, title: str = "Loading", style: str = 'dots'):
        """
        Initialize spinner

        Args:
            title: Title to display
            style: Spinner style (dots, line, arrow, blocks, simple)
        """
        self.title = title
        self.frames = self.SPINNERS.get(style, self.SPINNERS['dots'])
        self.current_frame = 0
        self.running = False
        self.start_time = time.time()

    def spin(self):
        """Advance to next frame"""
        elapsed = time.time() - self.start_time
        elapsed_str = f"{int(elapsed)}s"

        frame = self.frames[self.current_frame]
        output = f"\r{frame} {self.title}... ({elapsed_str})"

        sys.stdout.write(output)
        sys.stdout.flush()

        self.current_frame = (self.current_frame + 1) % len(self.frames)

    def stop(self, message: str = "Done"):
        """Stop spinner with final message"""
        sys.stdout.write(f"\r✓ {message}\n")
        sys.stdout.flush()


class MultiStageProgress:
    """Multi-stage progress tracker"""

    def __init__(self, stages: List[str]):
        """
        Initialize multi-stage progress

        Args:
            stages: List of stage names
        """
        self.stages = stages
        self.current_stage = 0
        self.total_stages = len(stages)
        self.stage_progress = {}
        self.start_time = time.time()

    def start_stage(self, stage_index: int):
        """Start a specific stage"""
        self.current_stage = stage_index
        self.stage_progress[stage_index] = {
            'start_time': time.time(),
            'status': 'in_progress'
        }
        self.render()

    def complete_stage(self, stage_index: int):
        """Mark stage as complete"""
        if stage_index in self.stage_progress:
            self.stage_progress[stage_index]['status'] = 'complete'
            self.stage_progress[stage_index]['end_time'] = time.time()
        self.render()

    def render(self) -> str:
        """Render multi-stage progress"""
        output = [
            "┌─────────────────────────────────────────────────────────────────┐",
            "│  PROGRESS                                                       │",
            "├─────────────────────────────────────────────────────────────────┤"
        ]

        for i, stage_name in enumerate(self.stages):
            if i in self.stage_progress:
                status = self.stage_progress[i]['status']
                if status == 'complete':
                    icon = "✓"
                elif status == 'in_progress':
                    icon = "▶"
                else:
                    icon = "○"
            else:
                icon = "○"

            # Calculate stage duration if complete
            duration_str = ""
            if i in self.stage_progress and status == 'complete':
                duration = self.stage_progress[i]['end_time'] - self.stage_progress[i]['start_time']
                duration_str = f" ({duration:.1f}s)"

            line = f"│  {icon} {stage_name}{duration_str}"
            output.append(f"{line:<65} │")

        # Overall progress
        completed = sum(1 for p in self.stage_progress.values() if p['status'] == 'complete')
        overall_pct = int((completed / self.total_stages) * 100)

        output.extend([
            "│                                                                 │",
            f"│  Overall: {overall_pct}% complete ({completed}/{self.total_stages} stages) {' '*20} │",
            "└─────────────────────────────────────────────────────────────────┘"
        ])

        result = "\n".join(output)
        print(result)
        return result


class ProgressIndicators:
    """Unified progress indicator manager"""

    @staticmethod
    def bar(total: int, title: str = "Progress", width: int = 50) -> ProgressBar:
        """Create progress bar"""
        return ProgressBar(total=total, title=title, width=width)

    @staticmethod
    def spinner(title: str = "Loading", style: str = 'dots') -> Spinner:
        """Create spinner"""
        return Spinner(title=title, style=style)

    @staticmethod
    def multi_stage(stages: List[str]) -> MultiStageProgress:
        """Create multi-stage progress"""
        return MultiStageProgress(stages=stages)

    @staticmethod
    def simple_progress(current: int, total: int, prefix: str = '') -> str:
        """Simple inline progress indicator"""
        percentage = int((current / total) * 100) if total > 0 else 0
        return f"{prefix}[{current}/{total}] {percentage}%"

    @staticmethod
    def download_progress(bytes_downloaded: int, total_bytes: int, speed_bps: Optional[float] = None) -> str:
        """Download progress indicator"""
        mb_down = bytes_downloaded / 1024 / 1024
        mb_total = total_bytes / 1024 / 1024
        percentage = int((bytes_downloaded / total_bytes) * 100) if total_bytes > 0 else 0

        speed_str = ""
        if speed_bps:
            speed_mbps = speed_bps / 1024 / 1024
            speed_str = f" @ {speed_mbps:.2f} MB/s"

        return f"Downloading: {mb_down:.2f}/{mb_total:.2f} MB ({percentage}%){speed_str}"

    @staticmethod
    def file_processing_progress(files_processed: int, total_files: int,
                                 current_file: Optional[str] = None) -> str:
        """File processing progress"""
        percentage = int((files_processed / total_files) * 100) if total_files > 0 else 0

        output = f"Processing: [{files_processed}/{total_files}] {percentage}%"
        if current_file:
            output += f" - {current_file}"

        return output


# Example usage functions
def example_progress_bar():
    """Example: Progress bar for file processing"""
    total_files = 50
    bar = ProgressIndicators.bar(total_files, "Processing files")

    for i in range(total_files):
        # Simulate work
        time.sleep(0.1)
        bar.update()

    bar.finish()


def example_spinner():
    """Example: Spinner for network operation"""
    spinner = ProgressIndicators.spinner("Connecting to server", style='dots')

    for _ in range(20):
        spinner.spin()
        time.sleep(0.1)

    spinner.stop("Connected successfully")


def example_multi_stage():
    """Example: Multi-stage operation"""
    stages = [
        "Loading configuration",
        "Connecting to database",
        "Fetching data",
        "Processing results",
        "Saving output"
    ]

    progress = ProgressIndicators.multi_stage(stages)

    for i, stage in enumerate(stages):
        progress.start_stage(i)
        time.sleep(1)  # Simulate work
        progress.complete_stage(i)


# Convenience functions
def create_progress_bar(total: int, title: str = "Progress") -> ProgressBar:
    """Quick progress bar creation"""
    return ProgressIndicators.bar(total, title)


def create_spinner(title: str = "Loading") -> Spinner:
    """Quick spinner creation"""
    return ProgressIndicators.spinner(title)
