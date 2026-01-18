"""
Policy Enforcer Service - Route Validation & Safety Checks

Validates routing decisions against the Offline-First policy.
Implements secret detection, privacy checks, and cost constraints.

Policy Rules:
  - Private data never leaves device/local
  - Secrets are detected and redacted before cloud transmission
  - Cost budgets are enforced
  - Cloud escalation is logged and tracked
  - User can disable cloud entirely

Features:
  - Secret detection (regex-based)
  - Privacy tier enforcement
  - Cost budget validation
  - Task audit logging
  - Policy override capability (for testing)

Usage:
    from wizard.services.policy_enforcer import PolicyEnforcer

    enforcer = PolicyEnforcer()
    is_valid, reason = enforcer.validate_route(
        task_id="t123",
        privacy="internal",
        backend="cloud",
        estimated_cost=0.05
    )

Version: 1.0.0
"""

import re
from dataclasses import dataclass
from datetime import datetime, date
from typing import Tuple, List, Dict, Any, Optional
from pathlib import Path
import json

from wizard.services.logging_manager import get_logger

logger = get_logger("policy-enforcer")


@dataclass
class PolicyViolation:
    """Describes a policy violation."""

    task_id: str
    rule: str
    reason: str
    severity: str  # "warning", "error"
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "rule": self.rule,
            "reason": self.reason,
            "severity": self.severity,
            "timestamp": self.timestamp,
        }


class PolicyEnforcer:
    """Validates routing decisions against policy."""

    # Secret patterns (simplified; improve as needed)
    SECRET_PATTERNS = {
        "api_key": r"(?i)(api[_-]?key|apikey|api_secret)['\"]?\s*[:=]\s*['\"]?[a-zA-Z0-9\-_]{32,}",
        "oauth_token": r"(?i)(oauth|access_token|refresh_token)['\"]?\s*[:=]\s*['\"]?[a-zA-Z0-9\-_.]{40,}",
        "aws_key": r"(?i)(AKIA|aws_access_key_id)['\"]?\s*[:=]\s*['\"]?[A-Z0-9]{20}",
        "private_key": r"(?i)(private[_-]?key|-----BEGIN)['\"]?\s*[:=]?\s*['\"]?[a-zA-Z0-9\+/=]{32,}",
        "password": r"(?i)(password)['\"]?\s*[:=]\s*['\"]?[^\s'\"]{8,}",
        "database_url": r"(?i)(database[_-]?url|db[_-]?url|connectionstring)['\"]?\s*[:=]\s*['\"]?[^\s'\"]+",
        "bearer_token": r"Bearer\s+[a-zA-Z0-9\-_.]{20,}",
    }

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize policy enforcer.

        Args:
            config_path: Path to policy config
        """
        self.config_path = config_path or Path("wizard/config/policy.json")
        self.violations: List[PolicyViolation] = []
        self.today_cloud_cost = 0.0
        self._load_config()

    def _load_config(self) -> None:
        """Load policy configuration."""
        self.config = {
            "cloud_enabled": False,  # Disabled by default
            "daily_budget_usd": 10.0,
            "monthly_budget_usd": 200.0,
            "detect_secrets": True,
            "redact_secrets": True,
            "require_privacy_declaration": True,
            "log_violations": True,
        }

        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    self.config.update(json.load(f))
                logger.info("[LOCAL] Loaded policy config")
            except Exception as e:
                logger.error(f"[LOCAL] Failed to load policy config: {e}")

    def validate_route(
        self,
        task_id: str,
        privacy: str,
        backend: str,
        estimated_cost: float = 0.0,
        prompt: str = "",
    ) -> Tuple[bool, Optional[str]]:
        """Validate a routing decision against policy.

        Args:
            task_id: Task identifier
            privacy: Privacy level ("private", "internal", "public")
            backend: Backend name ("ollama", "openrouter")
            estimated_cost: Estimated cost if cloud
            prompt: The prompt (for secret detection)

        Returns:
            Tuple[is_valid, reason]
            - is_valid: True if route is permitted
            - reason: Error message if invalid, else None
        """
        violations = []

        # Rule 1: Private tasks MUST stay local
        if privacy.lower() == "private" and backend != "ollama":
            violations.append(f"Private tasks cannot use {backend} backend")
            self._record_violation(
                task_id, "privacy_enforcement", violations[0], "error"
            )

        # Rule 2: Cloud escalation requires explicit enable
        if backend != "ollama" and not self.config["cloud_enabled"]:
            violations.append(
                "Cloud backend is disabled. Set cloud_enabled=true to allow cloud escalation."
            )
            self._record_violation(task_id, "cloud_disabled", violations[-1], "error")

        # Rule 3: Secret detection
        if self.config["detect_secrets"] and prompt:
            secrets = self._detect_secrets(prompt)
            if secrets and backend != "ollama":
                violations.append(
                    f"Detected secrets in prompt: {', '.join(secrets)}. "
                    "Cannot escalate to cloud without redaction."
                )
                self._record_violation(
                    task_id, "secrets_detected", violations[-1], "error"
                )

        # Rule 4: Daily budget enforcement
        if backend != "ollama":
            today = date.today().isoformat()
            if self.today_cloud_cost + estimated_cost > self.config["daily_budget_usd"]:
                violations.append(
                    f"Daily budget exceeded. Current: ${self.today_cloud_cost:.2f}, "
                    f"Request: ${estimated_cost:.2f}, Limit: ${self.config['daily_budget_usd']}"
                )
                self._record_violation(
                    task_id, "budget_exceeded", violations[-1], "warning"
                )

        if violations:
            return False, "; ".join(violations)

        return True, None

    def _detect_secrets(self, text: str) -> List[str]:
        """Detect potential secrets in text.

        Args:
            text: Text to scan

        Returns:
            List of secret types detected
        """
        detected = []
        for secret_type, pattern in self.SECRET_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(secret_type)
                logger.warning(f"[LOCAL] Detected {secret_type} in text")
        return detected

    def redact_secrets(self, text: str) -> str:
        """Redact detected secrets from text.

        Args:
            text: Text to redact

        Returns:
            Text with secrets replaced with [REDACTED:type]
        """
        result = text
        for secret_type, pattern in self.SECRET_PATTERNS.items():
            result = re.sub(
                pattern, f"[REDACTED:{secret_type}]", result, flags=re.IGNORECASE
            )
        return result

    def _record_violation(
        self, task_id: str, rule: str, reason: str, severity: str
    ) -> None:
        """Record a policy violation.

        Args:
            task_id: Task that violated policy
            rule: Policy rule violated
            reason: Description of violation
            severity: "warning" or "error"
        """
        violation = PolicyViolation(
            task_id=task_id,
            rule=rule,
            reason=reason,
            severity=severity,
            timestamp=datetime.utcnow().isoformat(),
        )
        self.violations.append(violation)

        if self.config["log_violations"]:
            log_func = logger.warning if severity == "warning" else logger.error
            log_func(f"[POLICY] {rule}: {reason}")

    def record_cloud_cost(self, amount_usd: float) -> None:
        """Record a cloud API cost toward daily budget.

        Args:
            amount_usd: Amount in USD
        """
        self.today_cloud_cost += amount_usd
        logger.info(
            f"[WIZ] Recorded cloud cost: ${amount_usd:.4f} (daily total: ${self.today_cloud_cost:.2f})"
        )

    def reset_daily_budget(self) -> None:
        """Reset daily cost tracking (call once per day)."""
        self.today_cloud_cost = 0.0
        logger.info("[WIZ] Daily budget reset")

    def get_policy_status(self) -> Dict[str, Any]:
        """Get current policy status.

        Returns:
            Dict with policy state and violations
        """
        return {
            "cloud_enabled": self.config["cloud_enabled"],
            "daily_budget": self.config["daily_budget_usd"],
            "today_spent": self.today_cloud_cost,
            "today_remaining": self.config["daily_budget_usd"] - self.today_cloud_cost,
            "monthly_budget": self.config["monthly_budget_usd"],
            "total_violations": len(self.violations),
            "recent_violations": [v.to_dict() for v in self.violations[-5:]],
        }
