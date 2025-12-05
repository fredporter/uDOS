"""
uDOS v1.1.0 - API Usage Audit Logger

Tracks all external API calls (Gemini, web access, etc.) for security and cost monitoring.

Features:
- Role-based access logging
- Token usage tracking
- Cost estimation
- Query pattern analysis
- Compliance and security audit trail

Version: 1.1.0
Status: Foundation - Active Development
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class APICallRecord:
    """Record of an external API call"""
    timestamp: str
    user_role: str
    operation: str  # 'OK ASK', 'OK DEV', 'FETCH', etc.
    api_type: str  # 'gemini', 'web', 'github'
    query: str  # First 100 chars for privacy
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    duration_ms: Optional[float] = None
    success: bool = True
    error_msg: Optional[str] = None
    context: Optional[Dict] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {k: v for k, v in asdict(self).items() if v is not None}


class APIAuditLogger:
    """
    Audit logger for external API calls.

    Logs all API usage to memory/logs/audit.log with:
    - Timestamp and user role
    - Operation and API type
    - Token usage and cost
    - Query details (truncated for privacy)
    - Success/failure status
    """

    def __init__(self, log_dir: str = "memory/logs"):
        """
        Initialize audit logger.

        Args:
            log_dir: Directory for audit logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Main audit log file
        self.audit_file = self.log_dir / "audit.log"

        # JSON log for detailed analysis
        self.audit_json = self.log_dir / "audit.json"

        # Session records
        self.session_records: List[APICallRecord] = []

        # Initialize files if they don't exist
        if not self.audit_file.exists():
            self.audit_file.touch()
        if not self.audit_json.exists():
            with open(self.audit_json, 'w') as f:
                json.dump({"records": []}, f)

    def log_api_call(
        self,
        user_role: str,
        operation: str,
        api_type: str,
        query: str,
        tokens_used: Optional[int] = None,
        cost_estimate: Optional[float] = None,
        duration_ms: Optional[float] = None,
        success: bool = True,
        error_msg: Optional[str] = None,
        context: Optional[Dict] = None
    ):
        """
        Log an external API call.

        Args:
            user_role: User's role (wizard, user, power, root)
            operation: Command that triggered API call
            api_type: Type of API (gemini, web, github)
            query: Query text (will be truncated)
            tokens_used: Number of tokens consumed
            cost_estimate: Estimated cost in USD
            duration_ms: Call duration in milliseconds
            success: Whether call succeeded
            error_msg: Error message if failed
            context: Additional context
        """
        # Truncate query for privacy
        query_safe = query[:100] + "..." if len(query) > 100 else query

        record = APICallRecord(
            timestamp=datetime.now().isoformat(),
            user_role=user_role,
            operation=operation,
            api_type=api_type,
            query=query_safe,
            tokens_used=tokens_used,
            cost_estimate=cost_estimate,
            duration_ms=duration_ms,
            success=success,
            error_msg=error_msg,
            context=context
        )

        self.session_records.append(record)

        # Write to text log (human-readable)
        self._write_text_log(record)

        # Write to JSON log (machine-readable)
        self._write_json_log(record)

    def _write_text_log(self, record: APICallRecord):
        """Write human-readable log entry"""
        status = "✓" if record.success else "✗"
        cost_str = f"${record.cost_estimate:.5f}" if record.cost_estimate else "N/A"
        tokens_str = f"{record.tokens_used} tokens" if record.tokens_used else "N/A"

        log_line = (
            f"[{record.timestamp}] {status} "
            f"role={record.user_role} "
            f"op={record.operation} "
            f"api={record.api_type} "
            f"tokens={tokens_str} "
            f"cost={cost_str} "
            f"query=\"{record.query}\""
        )

        if record.error_msg:
            log_line += f" error=\"{record.error_msg}\""

        with open(self.audit_file, 'a') as f:
            f.write(log_line + "\n")

    def _write_json_log(self, record: APICallRecord):
        """Write JSON log entry"""
        try:
            # Read existing records
            with open(self.audit_json, 'r') as f:
                data = json.load(f)

            # Append new record
            data['records'].append(record.to_dict())

            # Write back
            with open(self.audit_json, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            # If JSON write fails, log to text file
            with open(self.audit_file, 'a') as f:
                f.write(f"[ERROR] Failed to write JSON log: {e}\n")

    def get_session_summary(self) -> Dict:
        """
        Get summary of current session's API usage.

        Returns:
            Dict with usage statistics
        """
        if not self.session_records:
            return {
                "total_calls": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "by_operation": {},
                "by_api": {},
                "success_rate": 0.0
            }

        total_tokens = sum(r.tokens_used or 0 for r in self.session_records)
        total_cost = sum(r.cost_estimate or 0.0 for r in self.session_records)
        successful = sum(1 for r in self.session_records if r.success)

        # Group by operation
        by_operation = {}
        for record in self.session_records:
            by_operation[record.operation] = by_operation.get(record.operation, 0) + 1

        # Group by API type
        by_api = {}
        for record in self.session_records:
            by_api[record.api_type] = by_api.get(record.api_type, 0) + 1

        return {
            "total_calls": len(self.session_records),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "by_operation": by_operation,
            "by_api": by_api,
            "success_rate": successful / len(self.session_records) if self.session_records else 0.0
        }

    def format_session_summary(self) -> str:
        """
        Format session summary for display.

        Returns:
            Formatted string with API usage statistics
        """
        summary = self.get_session_summary()

        if summary['total_calls'] == 0:
            return "📊 API Usage: No API calls this session"

        output = f"""📊 API Usage Summary (This Session)
{"=" * 60}

Total Calls: {summary['total_calls']}
Total Tokens: {summary['total_tokens']:,}
Estimated Cost: ${summary['total_cost']:.5f}
Success Rate: {summary['success_rate']:.1%}

By Operation:"""

        for op, count in sorted(summary['by_operation'].items(), key=lambda x: x[1], reverse=True):
            output += f"\n  • {op}: {count}"

        output += "\n\nBy API Type:"
        for api, count in sorted(summary['by_api'].items(), key=lambda x: x[1], reverse=True):
            output += f"\n  • {api}: {count}"

        return output


# Global audit logger instance
_audit_logger: Optional[APIAuditLogger] = None


def get_audit_logger() -> APIAuditLogger:
    """Get or create global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = APIAuditLogger()
    return _audit_logger


def log_api_call(user_role: str, operation: str, api_type: str, query: str,
                tokens: int = None, cost: float = None, duration_ms: float = None,
                success: bool = True, error: str = None):
    """
    Convenience function to log API calls.

    Usage:
        log_api_call("wizard", "OK ASK", "gemini", "How do I...", tokens=150, cost=0.00045)
    """
    logger = get_audit_logger()
    logger.log_api_call(
        user_role=user_role,
        operation=operation,
        api_type=api_type,
        query=query,
        tokens_used=tokens,
        cost_estimate=cost,
        duration_ms=duration_ms,
        success=success,
        error_msg=error
    )
