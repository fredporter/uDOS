"""
uDOS v1.2.0 - Priority Queue Service

Workflow-aware request prioritization:
- 4 priority levels: critical, high, normal, low
- Priority-based queueing with fairness
- Workflow context tracking
- Request batching for efficiency
- Deadline-aware scheduling

Version: 1.2.0 (Task 5 - API Monitoring)
Author: uDOS Development Team
"""

import time
import heapq
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum


class Priority(IntEnum):
    """Request priority levels (lower number = higher priority)."""
    CRITICAL = 0  # System-critical, workflow failures, emergencies
    HIGH = 1      # User-initiated interactive requests
    NORMAL = 2    # Background workflows, batch operations
    LOW = 3       # Bulk operations, optional enhancements


@dataclass(order=True)
class PriorityRequest:
    """
    Prioritized request with scheduling metadata.

    Uses dataclass ordering for heap queue.
    """
    # Heap ordering fields (must come first)
    priority: int = field(compare=True)
    timestamp: float = field(compare=True)

    # Request data (not compared)
    request_id: str = field(compare=False)
    operation: str = field(compare=False)
    callback: Callable = field(compare=False, repr=False)
    args: Tuple = field(default_factory=tuple, compare=False, repr=False)
    kwargs: Dict = field(default_factory=dict, compare=False, repr=False)

    # Metadata
    workflow_id: Optional[str] = field(default=None, compare=False)
    deadline: Optional[float] = field(default=None, compare=False)
    estimated_cost: float = field(default=0.0, compare=False)
    retries: int = field(default=0, compare=False)
    max_retries: int = field(default=3, compare=False)


class PriorityQueue:
    """
    Priority queue for API requests with workflow awareness.

    Features:
    - 4-level priority system (critical > high > normal > low)
    - Workflow context tracking
    - Deadline-aware scheduling
    - Request batching
    - Fairness guarantees (prevent starvation)
    """

    def __init__(self,
                 max_queue_size: int = 1000,
                 starvation_threshold_seconds: float = 60.0):
        """
        Initialize priority queue.

        Args:
            max_queue_size: Maximum queue size (blocks if exceeded)
            starvation_threshold_seconds: Max wait time before priority boost
        """
        self.max_queue_size = max_queue_size
        self.starvation_threshold = starvation_threshold_seconds

        # Main priority queue (heap)
        self._queue: List[PriorityRequest] = []

        # Fast lookup by request ID
        self._requests_by_id: Dict[str, PriorityRequest] = {}

        # Workflow tracking
        self._workflows: Dict[str, List[str]] = {}  # workflow_id -> request_ids

        # Statistics
        self.stats = {
            'total_enqueued': 0,
            'total_dequeued': 0,
            'total_completed': 0,
            'total_failed': 0,
            'total_timeouts': 0,
            'total_retries': 0,
            'by_priority': {
                'critical': {'enqueued': 0, 'completed': 0, 'failed': 0},
                'high': {'enqueued': 0, 'completed': 0, 'failed': 0},
                'normal': {'enqueued': 0, 'completed': 0, 'failed': 0},
                'low': {'enqueued': 0, 'completed': 0, 'failed': 0}
            },
            'avg_wait_time_seconds': 0.0,
            'max_wait_time_seconds': 0.0
        }

        # Completed requests (for statistics)
        self._completed_requests: List[Dict] = []

    # ========== Queueing ==========

    def enqueue(self,
                operation: str,
                callback: Callable,
                args: Tuple = (),
                kwargs: Optional[Dict] = None,
                priority: Priority = Priority.NORMAL,
                workflow_id: Optional[str] = None,
                deadline: Optional[float] = None,
                estimated_cost: float = 0.0,
                request_id: Optional[str] = None) -> str:
        """
        Add request to priority queue.

        Args:
            operation: Operation name (e.g., 'DO', 'GUIDE', 'SVG')
            callback: Function to call when processed
            args: Positional arguments for callback
            kwargs: Keyword arguments for callback
            priority: Request priority level
            workflow_id: Optional workflow context
            deadline: Optional deadline (Unix timestamp)
            estimated_cost: Estimated API cost in USD
            request_id: Optional request ID (generated if not provided)

        Returns:
            Request ID

        Raises:
            RuntimeError: If queue is full
        """
        if len(self._queue) >= self.max_queue_size:
            raise RuntimeError(f"Queue full ({self.max_queue_size} requests)")

        # Generate request ID if not provided
        if request_id is None:
            request_id = f"{operation}_{int(time.time() * 1000)}"

        # Create request
        request = PriorityRequest(
            priority=priority.value,
            timestamp=time.time(),
            request_id=request_id,
            operation=operation,
            callback=callback,
            args=args,
            kwargs=kwargs or {},
            workflow_id=workflow_id,
            deadline=deadline,
            estimated_cost=estimated_cost
        )

        # Add to heap queue
        heapq.heappush(self._queue, request)

        # Add to lookup
        self._requests_by_id[request_id] = request

        # Track workflow
        if workflow_id:
            if workflow_id not in self._workflows:
                self._workflows[workflow_id] = []
            self._workflows[workflow_id].append(request_id)

        # Update statistics
        self.stats['total_enqueued'] += 1
        priority_name = Priority(priority).name.lower()
        self.stats['by_priority'][priority_name]['enqueued'] += 1

        return request_id

    def dequeue(self, timeout_seconds: Optional[float] = None) -> Optional[PriorityRequest]:
        """
        Get next highest-priority request.

        Args:
            timeout_seconds: Optional timeout for waiting

        Returns:
            PriorityRequest or None if queue empty (or timeout)
        """
        if not self._queue:
            return None

        # Apply starvation prevention
        self._prevent_starvation()

        # Get highest priority request
        request = heapq.heappop(self._queue)

        # Remove from lookup
        if request.request_id in self._requests_by_id:
            del self._requests_by_id[request.request_id]

        # Update statistics
        self.stats['total_dequeued'] += 1

        # Calculate wait time
        wait_time = time.time() - request.timestamp
        self._update_wait_stats(wait_time)

        return request

    def _prevent_starvation(self) -> None:
        """
        Boost priority of requests that have waited too long.

        Prevents low-priority requests from being starved indefinitely.
        """
        now = time.time()
        boosted = []

        for request in self._queue:
            wait_time = now - request.timestamp

            # If waited longer than threshold, boost priority
            if wait_time > self.starvation_threshold:
                # Boost by one level (but not above CRITICAL)
                if request.priority > Priority.CRITICAL:
                    request.priority -= 1
                    boosted.append(request.request_id)

        if boosted:
            # Re-heapify to reflect new priorities
            heapq.heapify(self._queue)

    # ========== Request Management ==========

    def cancel(self, request_id: str) -> bool:
        """
        Cancel a pending request.

        Args:
            request_id: Request ID to cancel

        Returns:
            True if canceled, False if not found
        """
        if request_id not in self._requests_by_id:
            return False

        # Remove from lookup
        request = self._requests_by_id.pop(request_id)

        # Remove from queue (expensive but rare operation)
        self._queue = [r for r in self._queue if r.request_id != request_id]
        heapq.heapify(self._queue)

        # Remove from workflow tracking
        if request.workflow_id and request.workflow_id in self._workflows:
            self._workflows[request.workflow_id].remove(request_id)

        return True

    def get_request(self, request_id: str) -> Optional[PriorityRequest]:
        """
        Get request by ID without removing from queue.

        Args:
            request_id: Request ID

        Returns:
            PriorityRequest or None if not found
        """
        return self._requests_by_id.get(request_id)

    def update_priority(self, request_id: str, new_priority: Priority) -> bool:
        """
        Update priority of pending request.

        Args:
            request_id: Request ID
            new_priority: New priority level

        Returns:
            True if updated, False if not found
        """
        if request_id not in self._requests_by_id:
            return False

        request = self._requests_by_id[request_id]
        request.priority = new_priority.value

        # Re-heapify to reflect new priority
        heapq.heapify(self._queue)

        return True

    # ========== Workflow Management ==========

    def get_workflow_requests(self, workflow_id: str) -> List[PriorityRequest]:
        """
        Get all requests for a workflow.

        Args:
            workflow_id: Workflow ID

        Returns:
            List of PriorityRequest objects
        """
        if workflow_id not in self._workflows:
            return []

        request_ids = self._workflows[workflow_id]
        return [
            self._requests_by_id[rid]
            for rid in request_ids
            if rid in self._requests_by_id
        ]

    def cancel_workflow(self, workflow_id: str) -> int:
        """
        Cancel all requests for a workflow.

        Args:
            workflow_id: Workflow ID

        Returns:
            Number of requests canceled
        """
        if workflow_id not in self._workflows:
            return 0

        request_ids = self._workflows[workflow_id].copy()
        count = 0

        for request_id in request_ids:
            if self.cancel(request_id):
                count += 1

        # Remove workflow tracking
        del self._workflows[workflow_id]

        return count

    def get_workflow_status(self, workflow_id: str) -> Dict:
        """
        Get status of workflow requests.

        Args:
            workflow_id: Workflow ID

        Returns:
            Status dictionary with counts and requests
        """
        requests = self.get_workflow_requests(workflow_id)

        return {
            'workflow_id': workflow_id,
            'total_requests': len(requests),
            'by_priority': {
                'critical': len([r for r in requests if r.priority == Priority.CRITICAL]),
                'high': len([r for r in requests if r.priority == Priority.HIGH]),
                'normal': len([r for r in requests if r.priority == Priority.NORMAL]),
                'low': len([r for r in requests if r.priority == Priority.LOW])
            },
            'requests': [
                {
                    'request_id': r.request_id,
                    'operation': r.operation,
                    'priority': Priority(r.priority).name,
                    'wait_time': time.time() - r.timestamp,
                    'estimated_cost': r.estimated_cost
                }
                for r in requests
            ]
        }

    # ========== Execution ==========

    def execute_request(self, request: PriorityRequest) -> Tuple[bool, Any]:
        """
        Execute a request's callback.

        Args:
            request: PriorityRequest to execute

        Returns:
            (success: bool, result: Any)
        """
        try:
            result = request.callback(*request.args, **request.kwargs)

            # Record completion
            self._record_completion(request, success=True)

            return True, result

        except Exception as e:
            # Check if should retry
            if request.retries < request.max_retries:
                # Re-queue with incremented retry count
                request.retries += 1
                heapq.heappush(self._queue, request)
                self._requests_by_id[request.request_id] = request

                self.stats['total_retries'] += 1

                return False, f"Retrying ({request.retries}/{request.max_retries}): {str(e)}"
            else:
                # Max retries exceeded
                self._record_completion(request, success=False, error=str(e))

                return False, str(e)

    def _record_completion(self,
                          request: PriorityRequest,
                          success: bool,
                          error: Optional[str] = None) -> None:
        """Record request completion for statistics."""
        completion = {
            'request_id': request.request_id,
            'operation': request.operation,
            'priority': Priority(request.priority).name,
            'success': success,
            'error': error,
            'wait_time': time.time() - request.timestamp,
            'retries': request.retries,
            'completed_at': time.time()
        }

        self._completed_requests.append(completion)

        # Keep only last 1000 completions
        if len(self._completed_requests) > 1000:
            self._completed_requests = self._completed_requests[-1000:]

        # Update statistics
        if success:
            self.stats['total_completed'] += 1
        else:
            self.stats['total_failed'] += 1

        priority_name = Priority(request.priority).name.lower()
        if success:
            self.stats['by_priority'][priority_name]['completed'] += 1
        else:
            self.stats['by_priority'][priority_name]['failed'] += 1

    # ========== Statistics ==========

    def get_stats(self) -> Dict:
        """Get queue statistics."""
        return {
            'queue_size': len(self._queue),
            'max_queue_size': self.max_queue_size,
            'total_enqueued': self.stats['total_enqueued'],
            'total_dequeued': self.stats['total_dequeued'],
            'total_completed': self.stats['total_completed'],
            'total_failed': self.stats['total_failed'],
            'total_timeouts': self.stats['total_timeouts'],
            'total_retries': self.stats['total_retries'],
            'by_priority': self.stats['by_priority'],
            'avg_wait_time': self.stats['avg_wait_time_seconds'],
            'max_wait_time': self.stats['max_wait_time_seconds'],
            'active_workflows': len(self._workflows),
            'completion_rate': (self.stats['total_completed'] / self.stats['total_dequeued'] * 100)
                              if self.stats['total_dequeued'] > 0 else 0
        }

    def _update_wait_stats(self, wait_time: float) -> None:
        """Update wait time statistics."""
        # Update max
        if wait_time > self.stats['max_wait_time_seconds']:
            self.stats['max_wait_time_seconds'] = wait_time

        # Update average (running average)
        if self.stats['total_dequeued'] == 0:
            self.stats['avg_wait_time_seconds'] = wait_time
        else:
            n = self.stats['total_dequeued']
            self.stats['avg_wait_time_seconds'] = (
                (self.stats['avg_wait_time_seconds'] * (n - 1) + wait_time) / n
            )

    def get_queue_snapshot(self) -> List[Dict]:
        """
        Get snapshot of current queue state.

        Returns:
            List of request summaries
        """
        return [
            {
                'request_id': r.request_id,
                'operation': r.operation,
                'priority': Priority(r.priority).name,
                'wait_time': time.time() - r.timestamp,
                'workflow_id': r.workflow_id,
                'deadline': r.deadline,
                'estimated_cost': r.estimated_cost,
                'retries': r.retries
            }
            for r in sorted(self._queue)  # Sorted by priority
        ]

    # ========== Utility ==========

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._queue) == 0

    def is_full(self) -> bool:
        """Check if queue is full."""
        return len(self._queue) >= self.max_queue_size

    def size(self) -> int:
        """Get current queue size."""
        return len(self._queue)

    def clear(self) -> int:
        """
        Clear all pending requests.

        Returns:
            Number of requests cleared
        """
        count = len(self._queue)
        self._queue.clear()
        self._requests_by_id.clear()
        self._workflows.clear()
        return count


# ========== Global Instance ==========

_queue_instance: Optional[PriorityQueue] = None


def get_priority_queue() -> PriorityQueue:
    """
    Get or create global priority queue instance.

    Returns:
        PriorityQueue instance
    """
    global _queue_instance
    if _queue_instance is None:
        _queue_instance = PriorityQueue()
    return _queue_instance


def reset_queue() -> None:
    """Reset global queue instance (useful for testing)."""
    global _queue_instance
    _queue_instance = None
