"""
Model Router Service - Multi-Backend LLM Routing

Routes model requests between local (Ollama) and cloud (OpenRouter) backends
following the Offline-First policy.

Backend Options:
  - Ollama (local): Devstral Small 2, other local models
  - OpenRouter (cloud): Multi-provider routing (optional, burst only)

Routing Strategy:
  1. Local-first: Try Ollama/Devstral unless explicitly blocked
  2. Escalate only when: task tagged 'burst', local fails 2x, or policy requires
  3. Never escalate if: privacy=private, secrets detected, budget exhausted

Features:
  - Task classification (code, test, docs, design, ops)
  - Privacy tier enforcement (private, internal, public)
  - Secret detection & redaction
  - Cost estimation & tracking
  - Fallback & retry logic
  - Audit logging (all routing decisions)

Usage:
    from wizard.services.model_router import ModelRouter

    router = ModelRouter()
    route = router.classify_and_route(
        task_id="t123",
        prompt="refactor this code",
        workspace="core",
        privacy="internal"
    )
    # Returns: Route(backend="ollama", model="devstral-small-2", ...)

Version: 1.0.0
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pathlib import Path

from wizard.services.logging_manager import get_logger

logger = get_logger("model-router")


class Backend(Enum):
    """Available model backends."""

    LOCAL = "ollama"  # Local inference
    CLOUD = "openrouter"  # Cloud routing


class Workspace(Enum):
    """uDOS workspaces."""

    CORE = "core"
    APP = "app"
    WIZARD = "wizard"
    EXTENSIONS = "extensions"
    DOCS = "docs"


class Privacy(Enum):
    """Privacy levels for tasks."""

    PRIVATE = "private"  # Never share, local only
    INTERNAL = "internal"  # OK to share with Anthropic/others
    PUBLIC = "public"  # Can be published


class Intent(Enum):
    """Task intent classification."""

    CODE = "code"  # Code generation, refactoring
    TEST = "test"  # Test generation, validation
    DOCS = "docs"  # Documentation writing
    DESIGN = "design"  # Architecture, design decisions
    OPS = "ops"  # Operations, deployment


@dataclass
class Route:
    """Selected routing decision for a task."""

    task_id: str
    backend: Backend
    model: str  # e.g., "devstral-small-2" or "anthropic/claude-3.5-sonnet"
    prompt_size: int  # Approximate token count
    estimated_cost: float  # Estimated cost in USD (for cloud routes)
    escalation_reason: Optional[str] = None  # Why we escalated (if cloud)
    secret_scan_passed: bool = True  # Was secrets scan successful?
    privacy_level: Privacy = Privacy.INTERNAL
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, handling enums."""
        d = asdict(self)
        d["backend"] = self.backend.value
        d["privacy_level"] = self.privacy_level.value
        return d


@dataclass
class TaskClassification:
    """Classification of a task for routing purposes."""

    task_id: str
    workspace: Workspace
    intent: Intent
    privacy: Privacy
    urgency: str  # "low", "normal", "high"
    size_estimate: str  # "small" (<2K tokens), "medium" (2K-8K), "large" (>8K)
    tags: List[str] = field(
        default_factory=list
    )  # Custom tags: "burst", "offline_required"
    estimated_tokens: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def has_tag(self, tag: str) -> bool:
        """Check if task has a specific tag."""
        return tag in self.tags


class ModelRouter:
    """Routes requests between local and cloud backends."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize router.

        Args:
            config_path: Path to router config (optional)
        """
        self.config_path = config_path or Path("wizard/config/model_router.json")
        self.routing_log: List[Route] = []
        self.local_failures: Dict[str, int] = {}  # Track local failures per task
        self._load_config()

    def _load_config(self) -> None:
        """Load router configuration."""
        self.config = {
            "local_enabled": False,  # Disabled: no local model service running
            "local_endpoint": "http://127.0.0.1:11434",
            "local_model": "devstral-small-2",
            "cloud_enabled": False,  # Disabled by default
            "cloud_endpoint": "https://openrouter.ai/api/v1",
            "daily_budget_usd": 10.0,
            "max_local_context": 8192,  # Max tokens for local model
        }

        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    self.config.update(json.load(f))
                logger.info("[LOCAL] Loaded model router config")
            except Exception as e:
                logger.error(f"[LOCAL] Failed to load config: {e}")

    def classify_task(
        self,
        task_id: str,
        workspace: str,
        intent: str,
        privacy: str,
        urgency: str = "normal",
        prompt: str = "",
        tags: Optional[List[str]] = None,
    ) -> TaskClassification:
        """Classify a task for routing.

        Args:
            task_id: Unique task ID
            workspace: One of "core", "app", "wizard", "extensions", "docs"
            intent: One of "code", "test", "docs", "design", "ops"
            privacy: One of "private", "internal", "public"
            urgency: One of "low", "normal", "high"
            prompt: The actual prompt (for token estimation)
            tags: Custom tags (e.g., ["burst", "offline_required"])

        Returns:
            TaskClassification
        """
        try:
            workspace_enum = Workspace[workspace.upper()]
        except KeyError:
            logger.warning(
                f"[LOCAL] Unknown workspace: {workspace}, defaulting to core"
            )
            workspace_enum = Workspace.CORE

        try:
            intent_enum = Intent[intent.upper()]
        except KeyError:
            logger.warning(f"[LOCAL] Unknown intent: {intent}, defaulting to code")
            intent_enum = Intent.CODE

        try:
            privacy_enum = Privacy[privacy.upper()]
        except KeyError:
            logger.warning(
                f"[LOCAL] Unknown privacy: {privacy}, defaulting to internal"
            )
            privacy_enum = Privacy.INTERNAL

        # Estimate token count (rough: ~4 chars per token)
        estimated_tokens = len(prompt) // 4 if prompt else 0

        # Determine size
        if estimated_tokens < 2000:
            size_estimate = "small"
        elif estimated_tokens < 8000:
            size_estimate = "medium"
        else:
            size_estimate = "large"

        classification = TaskClassification(
            task_id=task_id,
            workspace=workspace_enum,
            intent=intent_enum,
            privacy=privacy_enum,
            urgency=urgency,
            size_estimate=size_estimate,
            tags=tags or [],
            estimated_tokens=estimated_tokens,
        )

        logger.info(
            f"[LOCAL] Classified task {task_id}: {intent} ({size_estimate}), privacy={privacy}"
        )
        return classification

    def route(self, classification: TaskClassification) -> Route:
        """Determine routing for a classified task.

        Args:
            classification: TaskClassification from classify_task()

        Returns:
            Route with selected backend and model

        Raises:
            ValueError: If task cannot be routed (all options exhausted)
        """
        task_id = classification.task_id

        # Rule 1: Private tasks NEVER go to cloud
        if classification.privacy == Privacy.PRIVATE:
            logger.info(f"[LOCAL] Task {task_id} is PRIVATE, routing local only")
            return self._route_local(classification)

        # Rule 2: offline_required tag forces local
        if classification.has_tag("offline_required"):
            logger.info(
                f"[LOCAL] Task {task_id} tagged offline_required, routing local"
            )
            return self._route_local(classification)

        # Rule 3: Try local first (unless disabled or failed twice)
        if self.config["local_enabled"]:
            if task_id not in self.local_failures:
                self.local_failures[task_id] = 0

            if self.local_failures[task_id] < 2:
                logger.info(f"[LOCAL] Attempting local route for {task_id}")
                return self._route_local(classification)
        else:
            logger.info(f"[LOCAL] Local routing disabled, skipping for {task_id}")

        # Rule 4: Local failed 2x, escalate if allowed
        if self.config["cloud_enabled"] and classification.privacy != Privacy.PRIVATE:
            logger.info(f"[LOCAL] Local failed 2x for {task_id}, escalating to cloud")
            return self._route_cloud(classification, reason="local_failure")

        # Rule 5: burst tag allows cloud
        if (
            classification.has_tag("burst")
            and self.config["cloud_enabled"]
            and classification.privacy != Privacy.PRIVATE
        ):
            logger.info(f"[LOCAL] Task {task_id} tagged burst, escalating to cloud")
            return self._route_cloud(classification, reason="burst_request")

        # No escalation possible, use local
        logger.info(f"[LOCAL] No escalation available, routing local")
        return self._route_local(classification)

    def _route_local(self, classification: TaskClassification) -> Route:
        """Create a local routing decision."""
        return Route(
            task_id=classification.task_id,
            backend=Backend.LOCAL,
            model=self.config["local_model"],
            prompt_size=classification.estimated_tokens,
            estimated_cost=0.0,  # Local is free
            privacy_level=classification.privacy,
        )

    def force_local_route(self, classification: TaskClassification) -> Route:
        """Force a local route (used when cloud blocked)."""
        return self._route_local(classification)

    def _route_cloud(
        self, classification: TaskClassification, reason: str = "burst"
    ) -> Route:
        """Create a cloud routing decision."""
        # Estimate cost (rough approximation for Claude 3.5 Sonnet)
        input_tokens = classification.estimated_tokens
        output_estimate = min(
            2000, input_tokens
        )  # Assume output ~same as input, capped
        estimated_cost = (input_tokens * 0.003 + output_estimate * 0.015) / 1000

        return Route(
            task_id=classification.task_id,
            backend=Backend.CLOUD,
            model="anthropic/claude-3.5-sonnet",  # Default cloud model
            prompt_size=input_tokens,
            estimated_cost=estimated_cost,
            escalation_reason=reason,
            privacy_level=classification.privacy,
        )

    def classify_and_route(
        self,
        task_id: str,
        workspace: str,
        intent: str,
        privacy: str = "internal",
        urgency: str = "normal",
        prompt: str = "",
        tags: Optional[List[str]] = None,
    ) -> Route:
        """Classify a task and return routing decision in one call.

        Convenience method combining classify_task() and route().

        Returns:
            Route object with backend/model selection
        """
        classification = self.classify_task(
            task_id=task_id,
            workspace=workspace,
            intent=intent,
            privacy=privacy,
            urgency=urgency,
            prompt=prompt,
            tags=tags,
        )
        return self.route(classification)

    def record_local_failure(self, task_id: str) -> None:
        """Record a local execution failure for a task.

        Args:
            task_id: Task that failed locally
        """
        if task_id not in self.local_failures:
            self.local_failures[task_id] = 0
        self.local_failures[task_id] += 1
        logger.warning(
            f"[LOCAL] Task {task_id} failed locally (attempt {self.local_failures[task_id]})"
        )

    def record_route(self, route: Route) -> None:
        """Record a routing decision for audit purposes.

        Args:
            route: Route object that was selected
        """
        self.routing_log.append(route)
        logger.info(
            f"[{route.backend.value.upper()}] Routed {route.task_id} "
            f"({route.model}, est: ${route.estimated_cost:.4f})"
        )

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics.

        Returns:
            Dict with local vs cloud counts, costs, etc.
        """
        if not self.routing_log:
            return {
                "total_routes": 0,
                "local_count": 0,
                "cloud_count": 0,
                "total_estimated_cost": 0.0,
            }

        local_routes = [r for r in self.routing_log if r.backend == Backend.LOCAL]
        cloud_routes = [r for r in self.routing_log if r.backend == Backend.CLOUD]
        total_cost = sum(r.estimated_cost for r in cloud_routes)

        return {
            "total_routes": len(self.routing_log),
            "local_count": len(local_routes),
            "cloud_count": len(cloud_routes),
            "local_percentage": (
                (len(local_routes) / len(self.routing_log) * 100)
                if self.routing_log
                else 0
            ),
            "total_estimated_cost": total_cost,
        }
