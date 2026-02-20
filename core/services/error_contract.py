"""Error handling contract for Core command failures."""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from core.services.logging_manager import get_logger

logger = get_logger("error-contract")


@dataclass
class CommandError(Exception):
    """Structured error for user-facing command failures."""

    code: str
    message: str
    recovery_hint: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    cause: Optional[Exception] = None
    level: str = "ERROR"

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def with_recovery(self, hint: str) -> "CommandError":
        """Chainable method to add recovery guidance."""
        self.recovery_hint = hint
        return self

    def to_log(self) -> Dict[str, Any]:
        """Safe logging representation (no sensitive data)."""
        return {
            "error_code": self.code,
            "message": self.message,
            "recovery_hint": self.recovery_hint,
            "details": self.details or {},
        }

    def log(self, log_target=None) -> None:
        """Log the error with a safe payload."""
        target = log_target or logger
        payload = self.to_log()
        level = (self.level or "ERROR").upper()
        if level == "INFO":
            target.info(self.message, extra=payload)
        elif level == "WARNING":
            target.warning(self.message, extra=payload)
        else:
            target.error(self.message, extra=payload)
