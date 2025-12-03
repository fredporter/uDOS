"""
Performance Monitoring Service v1.2.1

Tracks and validates v1.2.0 success criteria:
- Offline query rate (target: 90%+)
- API cost reduction (target: 99% vs old system)
- Response times (target: <500ms average)
- Rate limiting effectiveness
- Budget usage tracking

Integration with unified logging system (memory/logs/performance.log)

Version: 1.2.1
Author: uDOS Development Team
Date: 2025-12-03
"""

import time
import json
from pathlib import Path
from datetime import datetime, UTC
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from core.services.unified_logger import get_unified_logger, log_performance, log_system


@dataclass
class QueryMetric:
    """Individual query metric."""
    timestamp: str
    query_type: str  # generate, guide, svg, etc.
    mode: str  # offline, gemini, banana
    duration: float  # seconds
    cost: float  # USD
    confidence: Optional[float] = None  # 0-100 for offline queries
    tokens: Optional[int] = None  # Token count for online queries
    success: bool = True


class PerformanceMonitor:
    """Monitor and track performance metrics."""

    # Baseline costs (old ASSISTANT system for comparison)
    BASELINE_COST_PER_QUERY = 0.01  # $0.01 per query (estimated)

    def __init__(self, data_dir: str = "memory/logs"):
        """Initialize performance monitor.

        Args:
            data_dir: Directory for performance data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_unified_logger()

        # Current session metrics
        self.session_metrics: List[QueryMetric] = []
        self.session_start = datetime.now(UTC)

        # Load historical data
        self.historical_file = self.data_dir / "performance-history.json"
        self.historical_data = self._load_historical()

        log_system("Performance monitor initialized", level='info')

    def _load_historical(self) -> Dict[str, Any]:
        """Load historical performance data.

        Returns:
            Historical data dictionary
        """
        if self.historical_file.exists():
            try:
                with open(self.historical_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                log_system(f"Failed to load historical data: {e}", level='warning')

        return {
            'total_queries': 0,
            'offline_queries': 0,
            'online_queries': 0,
            'total_cost': 0.0,
            'total_time': 0.0,
            'sessions': []
        }

    def _save_historical(self):
        """Save historical performance data."""
        try:
            with open(self.historical_file, 'w') as f:
                json.dump(self.historical_data, f, indent=2)
        except Exception as e:
            log_system(f"Failed to save historical data: {e}", level='error')

    def track_query(self, query_type: str, mode: str, duration: float,
                   cost: float = 0.0, confidence: Optional[float] = None,
                   tokens: Optional[int] = None, success: bool = True):
        """Track individual query.

        Args:
            query_type: Type of query (generate, guide, svg, etc.)
            mode: Execution mode (offline, gemini, banana)
            duration: Query duration in seconds
            cost: Query cost in USD
            confidence: Confidence score for offline queries (0-100)
            tokens: Token count for online queries
            success: Whether query succeeded
        """
        metric = QueryMetric(
            timestamp=datetime.now(UTC).isoformat(),
            query_type=query_type,
            mode=mode,
            duration=duration,
            cost=cost,
            confidence=confidence,
            tokens=tokens,
            success=success
        )

        self.session_metrics.append(metric)

        # Log to unified logger
        offline = (mode == 'offline')
        log_performance(query_type, duration, offline,
                       mode=mode, cost=cost, confidence=confidence, tokens=tokens)

        # Update historical data
        self.historical_data['total_queries'] += 1
        if offline:
            self.historical_data['offline_queries'] += 1
        else:
            self.historical_data['online_queries'] += 1
        self.historical_data['total_cost'] += cost
        self.historical_data['total_time'] += duration

    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics.

        Returns:
            Session statistics dictionary
        """
        if not self.session_metrics:
            return {
                'total_queries': 0,
                'offline_rate': 0.0,
                'avg_duration': 0.0,
                'total_cost': 0.0,
                'cost_savings': 0.0
            }

        total = len(self.session_metrics)
        offline_count = sum(1 for m in self.session_metrics if m.mode == 'offline')
        total_duration = sum(m.duration for m in self.session_metrics)
        total_cost = sum(m.cost for m in self.session_metrics)

        # Calculate what cost would have been with old system
        baseline_cost = total * self.BASELINE_COST_PER_QUERY

        return {
            'session_start': self.session_start.isoformat(),
            'session_duration': (datetime.now(UTC) - self.session_start).total_seconds(),
            'total_queries': total,
            'offline_queries': offline_count,
            'online_queries': total - offline_count,
            'offline_rate': offline_count / total if total > 0 else 0.0,
            'avg_duration': total_duration / total if total > 0 else 0.0,
            'total_duration': total_duration,
            'total_cost': total_cost,
            'baseline_cost': baseline_cost,
            'cost_savings': baseline_cost - total_cost,
            'cost_reduction_pct': ((baseline_cost - total_cost) / baseline_cost * 100) if baseline_cost > 0 else 0.0,
            'success_rate': sum(1 for m in self.session_metrics if m.success) / total if total > 0 else 0.0
        }

    def get_all_time_stats(self) -> Dict[str, Any]:
        """Get all-time statistics (historical + session).

        Returns:
            All-time statistics dictionary
        """
        total = self.historical_data['total_queries']
        offline = self.historical_data['offline_queries']
        total_cost = self.historical_data['total_cost']
        total_time = self.historical_data['total_time']

        baseline_cost = total * self.BASELINE_COST_PER_QUERY

        return {
            'total_queries': total,
            'offline_queries': offline,
            'online_queries': total - offline,
            'offline_rate': offline / total if total > 0 else 0.0,
            'avg_duration': total_time / total if total > 0 else 0.0,
            'total_duration': total_time,
            'total_cost': total_cost,
            'baseline_cost': baseline_cost,
            'cost_savings': baseline_cost - total_cost,
            'cost_reduction_pct': ((baseline_cost - total_cost) / baseline_cost * 100) if baseline_cost > 0 else 0.0,
            'sessions_count': len(self.historical_data.get('sessions', []))
        }

    def validate_success_criteria(self) -> Dict[str, Any]:
        """Validate v1.2.0 success criteria.

        Returns:
            Validation results with pass/fail for each criterion
        """
        stats = self.get_all_time_stats()
        session_stats = self.get_session_stats()

        # Criteria from v1.2.0 success metrics
        criteria = {
            'offline_rate_90': {
                'target': 0.90,
                'actual': stats['offline_rate'],
                'passed': stats['offline_rate'] >= 0.90,
                'description': 'Offline query rate ≥90%'
            },
            'cost_reduction_99': {
                'target': 99.0,
                'actual': stats['cost_reduction_pct'],
                'passed': stats['cost_reduction_pct'] >= 99.0,
                'description': 'Cost reduction ≥99%'
            },
            'avg_response_500ms': {
                'target': 0.500,
                'actual': stats['avg_duration'],
                'passed': stats['avg_duration'] < 0.500,
                'description': 'Average response time <500ms'
            }
        }

        # Calculate percentiles for current session
        if self.session_metrics:
            durations = sorted(m.duration for m in self.session_metrics)
            n = len(durations)
            p50 = durations[n // 2] if n > 0 else 0.0
            p95 = durations[int(n * 0.95)] if n > 0 else 0.0
            p99 = durations[int(n * 0.99)] if n > 0 else 0.0

            criteria['p95_response_500ms'] = {
                'target': 0.500,
                'actual': p95,
                'passed': p95 < 0.500,
                'description': 'P95 response time <500ms'
            }

        all_passed = all(c['passed'] for c in criteria.values())

        return {
            'criteria': criteria,
            'all_passed': all_passed,
            'session_stats': session_stats,
            'all_time_stats': stats,
            'timestamp': datetime.now(UTC).isoformat()
        }

    def generate_report(self) -> str:
        """Generate performance validation report.

        Returns:
            Formatted report string
        """
        validation = self.validate_success_criteria()
        session = validation['session_stats']
        all_time = validation['all_time_stats']
        criteria = validation['criteria']

        report = []
        report.append("=" * 80)
        report.append("  PERFORMANCE VALIDATION REPORT v1.2.1")
        report.append("=" * 80)
        report.append("")

        # Session stats
        report.append("SESSION STATISTICS")
        report.append("-" * 80)
        report.append(f"  Started: {session.get('session_start', 'N/A')}")
        report.append(f"  Duration: {session.get('session_duration', 0):.1f}s")
        report.append(f"  Total Queries: {session.get('total_queries', 0)}")
        report.append(f"  Offline: {session.get('offline_queries', 0)} ({session.get('offline_rate', 0)*100:.1f}%)")
        report.append(f"  Online: {session.get('online_queries', 0)}")
        report.append(f"  Avg Duration: {session.get('avg_duration', 0)*1000:.1f}ms")
        report.append(f"  Total Cost: ${session.get('total_cost', 0):.4f}")
        report.append(f"  Cost Savings: ${session.get('cost_savings', 0):.4f} ({session.get('cost_reduction_pct', 0):.1f}% reduction)")
        report.append("")

        # All-time stats
        report.append("ALL-TIME STATISTICS")
        report.append("-" * 80)
        report.append(f"  Total Queries: {all_time['total_queries']}")
        report.append(f"  Offline: {all_time['offline_queries']} ({all_time['offline_rate']*100:.1f}%)")
        report.append(f"  Online: {all_time['online_queries']}")
        report.append(f"  Avg Duration: {all_time['avg_duration']*1000:.1f}ms")
        report.append(f"  Total Cost: ${all_time['total_cost']:.4f}")
        report.append(f"  Cost Savings: ${all_time['cost_savings']:.4f} ({all_time['cost_reduction_pct']:.1f}% reduction)")
        report.append("")

        # Success criteria
        report.append("SUCCESS CRITERIA VALIDATION")
        report.append("-" * 80)
        for key, crit in criteria.items():
            status = "✅ PASS" if crit['passed'] else "❌ FAIL"
            if 'pct' in key or 'rate' in key:
                report.append(f"  {status} {crit['description']}")
                report.append(f"      Target: {crit['target']*100:.1f}%, Actual: {crit['actual']*100:.1f}%")
            else:
                report.append(f"  {status} {crit['description']}")
                report.append(f"      Target: {crit['target']*1000:.0f}ms, Actual: {crit['actual']*1000:.0f}ms")
        report.append("")

        overall = "✅ ALL CRITERIA MET" if validation['all_passed'] else "❌ SOME CRITERIA NOT MET"
        report.append(f"OVERALL: {overall}")
        report.append("=" * 80)

        return "\n".join(report)

    def end_session(self):
        """End current session and save data."""
        if self.session_metrics:
            session_data = {
                'start': self.session_start.isoformat(),
                'end': datetime.now(UTC).isoformat(),
                'stats': self.get_session_stats(),
                'metrics_count': len(self.session_metrics)
            }

            self.historical_data.setdefault('sessions', []).append(session_data)
            self._save_historical()

            log_system(f"Performance session ended: {len(self.session_metrics)} queries", level='info')


# Singleton instance
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get singleton performance monitor instance.

    Returns:
        PerformanceMonitor instance
    """
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor
