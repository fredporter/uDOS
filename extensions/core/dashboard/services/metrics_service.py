"""
System Metrics Service for Advanced Dashboard
Handles collection and management of system metrics
"""

import psutil
import time
from datetime import datetime
from threading import Thread, Lock
from collections import deque
import json

class SystemMetricsService:
    def __init__(self, history_size=60):  # 1 minute of history at 1s intervals
        self.history_size = history_size
        self.metrics_history = {
            'cpu': deque(maxlen=history_size),
            'memory': deque(maxlen=history_size),
            'disk': deque(maxlen=history_size),
            'network': deque(maxlen=history_size),
            'processes': deque(maxlen=history_size)
        }
        self.lock = Lock()
        self._running = False
        self._collection_thread = None

    def start_collection(self):
        """Start the metrics collection thread"""
        if not self._running:
            self._running = True
            self._collection_thread = Thread(target=self._collect_metrics)
            self._collection_thread.daemon = True
            self._collection_thread.start()

    def stop_collection(self):
        """Stop the metrics collection thread"""
        self._running = False
        if self._collection_thread:
            self._collection_thread.join()

    def _collect_metrics(self):
        """Continuously collect system metrics"""
        while self._running:
            metrics = self._get_current_metrics()

            with self.lock:
                for metric_type, value in metrics.items():
                    self.metrics_history[metric_type].append({
                        'timestamp': datetime.now().isoformat(),
                        'value': value
                    })

            time.sleep(1)  # Collect every second

    def _get_current_metrics(self):
        """Get current system metrics"""
        return {
            'cpu': {
                'percent': psutil.cpu_percent(interval=None),
                'count': psutil.cpu_count(),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'network': self._get_network_info(),
            'processes': self._get_process_info()
        }

    def _get_network_info(self):
        """Get network interface statistics"""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }

    def _get_process_info(self):
        """Get information about top processes"""
        processes = []
        for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
                          key=lambda p: p.info['cpu_percent'] or 0,
                          reverse=True)[:5]:
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes

    def get_latest_metrics(self):
        """Get the most recent metrics"""
        with self.lock:
            return {
                metric_type: list(history)[-1] if history else None
                for metric_type, history in self.metrics_history.items()
            }

    def get_metrics_history(self, metric_type=None):
        """Get historical metrics data"""
        with self.lock:
            if metric_type:
                return list(self.metrics_history.get(metric_type, []))
            return {
                metric_type: list(history)
                for metric_type, history in self.metrics_history.items()
            }

    def to_json(self, metrics):
        """Convert metrics to JSON string"""
        return json.dumps(metrics, default=str)
