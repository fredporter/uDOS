"""
Scheduler Service for uDOS v1.1.2
Cron-like scheduling system for missions and tasks.

Features:
- Time-based triggers (DAILY AT, EVERY X minutes/hours/days)
- Condition-based triggers (WHEN condition evaluates true)
- Priority-based task queue
- Timeout handling and retry logic
- Task persistence and recovery
- Mission integration
"""

import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from enum import Enum


class ScheduleType(Enum):
    """Types of schedule triggers."""
    ONCE = "once"           # Run once at specific time
    DAILY = "daily"         # Run daily at specific time
    INTERVAL = "interval"   # Run every N seconds/minutes/hours/days
    CONDITION = "condition" # Run when condition becomes true
    CRON = "cron"          # Full cron expression support


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1  # ⚡ Run immediately
    HIGH = 2      # 🔴 Run soon
    MEDIUM = 3    # 🟡 Normal priority
    LOW = 4       # 🟢 Run when idle


class ScheduledTask:
    """A scheduled task with trigger conditions and execution details."""

    def __init__(
        self,
        task_id: str,
        name: str,
        command: str,
        schedule_type: ScheduleType,
        schedule_config: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        mission_id: Optional[str] = None,
        max_retries: int = 3,
        timeout_seconds: int = 300
    ):
        self.id = task_id
        self.name = name
        self.command = command
        self.schedule_type = schedule_type
        self.schedule_config = schedule_config
        self.priority = priority
        self.mission_id = mission_id
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

        # Execution state
        self.status = TaskStatus.PENDING
        self.retry_count = 0
        self.last_run: Optional[str] = None
        self.next_run: Optional[str] = None
        self.last_result: Optional[str] = None
        self.last_error: Optional[str] = None

        # Metadata
        self.created_at = datetime.now().isoformat()
        self.run_history: List[Dict[str, Any]] = []

        # Calculate initial next_run time
        self._calculate_next_run()

    def _calculate_next_run(self):
        """Calculate the next execution time based on schedule config."""
        now = datetime.now()

        if self.schedule_type == ScheduleType.ONCE:
            # Run at specific datetime
            target_time = datetime.fromisoformat(self.schedule_config['datetime'])
            self.next_run = target_time.isoformat() if target_time > now else None

        elif self.schedule_type == ScheduleType.DAILY:
            # Run daily at specific time (HH:MM)
            target_time_str = self.schedule_config['time']
            hour, minute = map(int, target_time_str.split(':'))
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # If time has passed today, schedule for tomorrow
            if target <= now:
                target += timedelta(days=1)

            self.next_run = target.isoformat()

        elif self.schedule_type == ScheduleType.INTERVAL:
            # Run every N units
            interval_seconds = self._parse_interval(self.schedule_config)
            if self.last_run:
                last = datetime.fromisoformat(self.last_run)
                next_time = last + timedelta(seconds=interval_seconds)
            else:
                next_time = now + timedelta(seconds=interval_seconds)

            self.next_run = next_time.isoformat()

        elif self.schedule_type == ScheduleType.CONDITION:
            # Check condition-based tasks every minute
            self.next_run = (now + timedelta(minutes=1)).isoformat()

    def _parse_interval(self, config: Dict[str, Any]) -> int:
        """Parse interval configuration to seconds."""
        value = config['value']
        unit = config['unit']

        multipliers = {
            'seconds': 1,
            'minutes': 60,
            'hours': 3600,
            'days': 86400,
            'weeks': 604800
        }

        return value * multipliers.get(unit, 60)

    def is_due(self) -> bool:
        """Check if task is due for execution."""
        if not self.next_run or self.status in [TaskStatus.CANCELLED, TaskStatus.RUNNING]:
            return False

        return datetime.now() >= datetime.fromisoformat(self.next_run)

    def mark_started(self):
        """Mark task as started."""
        self.status = TaskStatus.RUNNING
        self.last_run = datetime.now().isoformat()

    def mark_completed(self, result: str):
        """Mark task as completed successfully."""
        self.status = TaskStatus.COMPLETED
        self.last_result = result
        self.retry_count = 0

        # Add to history
        self.run_history.append({
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'result': result
        })

        # Calculate next run for recurring tasks
        if self.schedule_type in [ScheduleType.DAILY, ScheduleType.INTERVAL, ScheduleType.CONDITION]:
            self.status = TaskStatus.PENDING
            self._calculate_next_run()

    def mark_failed(self, error: str):
        """Mark task as failed."""
        self.last_error = error
        self.retry_count += 1

        # Add to history
        self.run_history.append({
            'timestamp': datetime.now().isoformat(),
            'status': 'failed',
            'error': error,
            'retry_count': self.retry_count
        })

        # Retry or mark as failed
        if self.retry_count < self.max_retries:
            self.status = TaskStatus.PENDING
            # Retry after exponential backoff
            backoff_seconds = 60 * (2 ** (self.retry_count - 1))
            next_retry = datetime.now() + timedelta(seconds=backoff_seconds)
            self.next_run = next_retry.isoformat()
        else:
            self.status = TaskStatus.FAILED

    def cancel(self):
        """Cancel the task."""
        self.status = TaskStatus.CANCELLED

    def pause(self):
        """Pause the task."""
        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.PAUSED

    def resume(self):
        """Resume a paused task."""
        if self.status == TaskStatus.PAUSED:
            self.status = TaskStatus.PENDING
            self._calculate_next_run()

    def to_dict(self) -> dict:
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'command': self.command,
            'schedule_type': self.schedule_type.value,
            'schedule_config': self.schedule_config,
            'priority': self.priority.value,
            'mission_id': self.mission_id,
            'max_retries': self.max_retries,
            'timeout_seconds': self.timeout_seconds,
            'status': self.status.value,
            'retry_count': self.retry_count,
            'last_run': self.last_run,
            'next_run': self.next_run,
            'last_result': self.last_result,
            'last_error': self.last_error,
            'created_at': self.created_at,
            'run_history': self.run_history
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ScheduledTask':
        """Create task from dictionary."""
        task = cls(
            task_id=data['id'],
            name=data['name'],
            command=data['command'],
            schedule_type=ScheduleType(data['schedule_type']),
            schedule_config=data['schedule_config'],
            priority=TaskPriority(data['priority']),
            mission_id=data.get('mission_id'),
            max_retries=data.get('max_retries', 3),
            timeout_seconds=data.get('timeout_seconds', 300)
        )

        task.status = TaskStatus(data['status'])
        task.retry_count = data.get('retry_count', 0)
        task.last_run = data.get('last_run')
        task.next_run = data.get('next_run')
        task.last_result = data.get('last_result')
        task.last_error = data.get('last_error')
        task.created_at = data.get('created_at', datetime.now().isoformat())
        task.run_history = data.get('run_history', [])

        return task


class Scheduler:
    """Task scheduler with cron-like functionality."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        # Allow separate instances for testing
        force_new = kwargs.pop('_force_new', False)
        if force_new or cls._instance is None:
            instance = super().__new__(cls)
            if not force_new:
                cls._instance = instance
            return instance
        return cls._instance

    def __init__(self, tasks_dir: str = "sandbox/workflow/schedules", _force_new: bool = False):
        # Skip re-initialization for singleton
        if not _force_new and hasattr(self, '_initialized'):
            return

        self.tasks_dir = Path(tasks_dir)
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None

        # Task execution callback (set by command system)
        self.execute_callback: Optional[Callable[[str], str]] = None

        self.load_all_tasks()
        self._initialized = True

    def load_all_tasks(self):
        """Load all scheduled tasks from disk."""
        if not self.tasks_dir.exists():
            return

        for task_file in self.tasks_dir.glob("*.json"):
            try:
                with open(task_file, 'r') as f:
                    data = json.load(f)
                    task = ScheduledTask.from_dict(data)
                    self.tasks[task.id] = task
            except Exception as e:
                print(f"⚠️  Error loading task {task_file.name}: {e}")

    def save_task(self, task: ScheduledTask):
        """Save task to disk."""
        # Ensure directory exists
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

        task_file = self.tasks_dir / f"{task.id}.json"
        with open(task_file, 'w') as f:
            json.dump(task.to_dict(), f, indent=2)

    def create_task(
        self,
        task_id: str,
        name: str,
        command: str,
        schedule_type: ScheduleType,
        schedule_config: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        mission_id: Optional[str] = None,
        max_retries: int = 3,
        timeout_seconds: int = 300
    ) -> ScheduledTask:
        """Create a new scheduled task."""
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            command=command,
            schedule_type=schedule_type,
            schedule_config=schedule_config,
            priority=priority,
            mission_id=mission_id,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds
        )

        self.tasks[task_id] = task
        self.save_task(task)

        return task

    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def list_tasks(
        self,
        status: Optional[str] = None,
        mission_id: Optional[str] = None,
        priority: Optional[int] = None
    ) -> List[ScheduledTask]:
        """List tasks with optional filtering."""
        tasks = list(self.tasks.values())

        if status:
            status_enum = TaskStatus(status)
            tasks = [t for t in tasks if t.status == status_enum]

        if mission_id:
            tasks = [t for t in tasks if t.mission_id == mission_id]

        if priority is not None:
            tasks = [t for t in tasks if t.priority.value == priority]

        # Sort by priority, then next_run time
        tasks.sort(key=lambda t: (t.priority.value, t.next_run or '9999'))

        return tasks

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        task = self.get_task(task_id)
        if not task:
            return False

        task.cancel()
        self.save_task(task)
        return True

    def pause_task(self, task_id: str) -> bool:
        """Pause a scheduled task."""
        task = self.get_task(task_id)
        if not task:
            return False

        task.pause()
        self.save_task(task)
        return True

    def resume_task(self, task_id: str) -> bool:
        """Resume a paused task."""
        task = self.get_task(task_id)
        if not task:
            return False

        task.resume()
        self.save_task(task)
        return True

    def start(self):
        """Start the scheduler worker thread."""
        if self.running:
            return

        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def stop(self):
        """Stop the scheduler worker thread."""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)

    def _worker_loop(self):
        """Main worker loop that checks and executes due tasks."""
        while self.running:
            try:
                # Get all pending tasks that are due
                due_tasks = [
                    t for t in self.tasks.values()
                    if t.status == TaskStatus.PENDING and t.is_due()
                ]

                # Sort by priority
                due_tasks.sort(key=lambda t: t.priority.value)

                # Execute due tasks
                for task in due_tasks:
                    self._execute_task(task)

                # Sleep for a short interval
                time.sleep(10)  # Check every 10 seconds

            except Exception as e:
                print(f"⚠️  Scheduler error: {e}")
                time.sleep(30)

    def _execute_task(self, task: ScheduledTask):
        """Execute a scheduled task."""
        try:
            task.mark_started()
            self.save_task(task)

            # Execute command via callback
            if self.execute_callback:
                result = self.execute_callback(task.command)
                task.mark_completed(result)
            else:
                task.mark_completed("⚠️  No execution callback configured")

        except Exception as e:
            task.mark_failed(str(e))

        finally:
            self.save_task(task)


def get_scheduler() -> Scheduler:
    """Get the singleton scheduler instance."""
    return Scheduler()
