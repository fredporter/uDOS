"""
Task Classifier Service - Categorization for Routing

Classifies tasks by intent, size, privacy, and other attributes to guide
the Model Router in making routing decisions.

Classification Dimensions:
  - Intent: code, test, docs, design, ops
  - Privacy: private, internal, public
  - Size: small (<2K), medium (2K-8K), large (>8K)
  - Urgency: low, normal, high
  - Workspace: core, app, wizard, extensions, docs

Features:
  - Intent detection from prompt analysis
  - Token count estimation
  - Automatic privacy inference from content
  - Tagging system for special handling
  - Historical classification tracking

Usage:
    from wizard.services.task_classifier import TaskClassifier

    classifier = TaskClassifier()
    task_class = classifier.classify(
        task_id="t123",
        prompt="refactor the FileHandler class",
        workspace="core"
    )

Version: 1.0.0
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from wizard.services.logging_manager import get_logger

logger = get_logger("task-classifier")


class Intent(Enum):
    """Task intent types."""

    CODE = "code"  # Code generation, refactoring, implementation
    TEST = "test"  # Test generation, validation
    DOCS = "docs"  # Documentation writing
    DESIGN = "design"  # Architecture, decisions, design
    OPS = "ops"  # Operations, deployment, scripts


class Privacy(Enum):
    """Privacy levels."""

    PRIVATE = "private"  # Never share (credentials, personal data)
    INTERNAL = "internal"  # OK to share with AI providers (company internal)
    PUBLIC = "public"  # OK to publish


@dataclass
class TaskProfile:
    """Classification profile for a task."""

    task_id: str
    intent: Intent
    privacy: Privacy
    size: str  # "small", "medium", "large"
    urgency: str  # "low", "normal", "high"
    workspace: str  # "core", "app", "wizard", etc.
    token_estimate: int
    confidence: float  # 0.0-1.0
    tags: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "intent": self.intent.value,
            "privacy": self.privacy.value,
            "size": self.size,
            "urgency": self.urgency,
            "workspace": self.workspace,
            "token_estimate": self.token_estimate,
            "confidence": self.confidence,
            "tags": self.tags,
            "reasons": self.reasons,
            "timestamp": self.timestamp,
        }


class TaskClassifier:
    """Classifies tasks for routing decisions."""

    # Intent detection patterns
    INTENT_PATTERNS = {
        Intent.CODE: [
            r"(?i)(refactor|implement|fix|rewrite|generate code|write code)",
            r"(?i)(function|method|class|module|module)",
            r"(?i)(debug|improve|optimize|convert)",
        ],
        Intent.TEST: [
            r"(?i)(test|unit test|test case|pytest|assertion)",
            r"(?i)(mock|stub|fixture)",
            r"(?i)(coverage|validation)",
        ],
        Intent.DOCS: [
            r"(?i)(document|write.*guide|wiki|readme|docstring)",
            r"(?i)(explain|describe|specification)",
            r"(?i)(comment|annotation)",
        ],
        Intent.DESIGN: [
            r"(?i)(architecture|design|pattern|decision)",
            r"(?i)(approach|strategy|structure)",
            r"(?i)(api|interface|protocol)",
        ],
        Intent.OPS: [
            r"(?i)(deploy|build|install|script|automation)",
            r"(?i)(docker|container|devops)",
            r"(?i)(setup|configuration)",
        ],
    }

    # Privacy risk patterns
    PRIVATE_PATTERNS = [
        r"(?i)(password|secret|key|token|credential)",
        r"(?i)(api[_-]?key|oauth)",
        r"(?i)(private|confidential|sensitive)",
        r"(?i)(\$\w+\s*=)",  # Variable assignment (likely code with secrets)
        r"(?i)(bearer\s+[a-z0-9]+)",
    ]

    def __init__(self):
        """Initialize classifier."""
        self.classification_history: List[TaskProfile] = []

    def classify(
        self,
        task_id: str,
        prompt: str,
        workspace: str = "core",
        urgency: str = "normal",
        explicit_privacy: Optional[str] = None,
    ) -> TaskProfile:
        """Classify a task.

        Args:
            task_id: Unique task ID
            prompt: The task prompt/request
            workspace: Target workspace (core, app, etc.)
            urgency: Task urgency (low, normal, high)
            explicit_privacy: Override privacy detection (for testing)

        Returns:
            TaskProfile with classification
        """
        # Detect intent
        intent, intent_confidence = self._detect_intent(prompt)

        # Estimate tokens
        token_estimate = len(prompt) // 4

        # Determine size
        if token_estimate < 2000:
            size = "small"
        elif token_estimate < 8000:
            size = "medium"
        else:
            size = "large"

        # Detect privacy
        if explicit_privacy:
            privacy = Privacy[explicit_privacy.upper()]
            privacy_confidence = 1.0
        else:
            privacy, privacy_confidence = self._detect_privacy(prompt)

        # Generate tags
        tags = self._generate_tags(prompt, intent, size)

        # Build reasons
        reasons = [
            f"Intent: {intent.value} ({intent_confidence:.1%})",
            f"Privacy: {privacy.value} ({privacy_confidence:.1%})",
            f"Size: {size} ({token_estimate} tokens)",
        ]

        profile = TaskProfile(
            task_id=task_id,
            intent=intent,
            privacy=privacy,
            size=size,
            urgency=urgency,
            workspace=workspace,
            token_estimate=token_estimate,
            confidence=(intent_confidence + privacy_confidence) / 2,
            tags=tags,
            reasons=reasons,
        )

        self.classification_history.append(profile)
        logger.info(
            f"[LOCAL] Classified {task_id}: {intent.value}/{size}/{privacy.value} "
            f"({profile.confidence:.0%} confidence)"
        )

        return profile

    def _detect_intent(self, prompt: str) -> tuple[Intent, float]:
        """Detect task intent from prompt.

        Args:
            prompt: The task prompt

        Returns:
            Tuple[Intent, confidence]
        """
        scores = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, prompt))
            scores[intent] = matches

        if not any(scores.values()):
            # No patterns matched, default to code (most common)
            return Intent.CODE, 0.3

        best_intent = max(scores, key=scores.get)
        max_score = scores[best_intent]
        confidence = min(0.95, 0.5 + (max_score / 3) * 0.3)  # Cap at 0.95

        return best_intent, confidence

    def _detect_privacy(self, prompt: str) -> tuple[Privacy, float]:
        """Detect privacy level from prompt content.

        Args:
            prompt: The task prompt

        Returns:
            Tuple[Privacy, confidence]
        """
        private_matches = sum(
            1 for pattern in self.PRIVATE_PATTERNS if re.search(pattern, prompt)
        )

        if private_matches > 0:
            confidence = min(0.95, 0.6 + (private_matches / 5) * 0.3)
            return Privacy.PRIVATE, confidence

        # Check for internal/company indicators
        if re.search(r"(?i)(uDOS|core|wizard|internal)", prompt):
            return Privacy.INTERNAL, 0.7

        # Default to internal for now (conservative)
        return Privacy.INTERNAL, 0.5

    def _generate_tags(self, prompt: str, intent: Intent, size: str) -> List[str]:
        """Generate tags for special handling.

        Args:
            prompt: The task prompt
            intent: Detected intent
            size: Size category

        Returns:
            List of tags
        """
        tags = []

        # Size-based tags
        if size == "large":
            tags.append("long_context")

        # Urgency-based tags
        if re.search(r"(?i)(urgent|asap|blocking|critical)", prompt):
            tags.append("urgent")

        # Tool-heavy tasks
        if re.search(r"(?i)(file|database|api|network|io)", prompt):
            tags.append("tooling_heavy")

        # Offline-only tasks
        if re.search(r"(?i)(offline|local|no.*internet|no.*network)", prompt):
            tags.append("offline_required")

        return tags

    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics.

        Returns:
            Dict with intent distribution, privacy breakdown, etc.
        """
        if not self.classification_history:
            return {
                "total_classified": 0,
                "intents": {},
                "privacy_levels": {},
                "avg_confidence": 0.0,
            }

        intents = {}
        privacy_levels = {}
        total_confidence = 0.0

        for profile in self.classification_history:
            intent_key = profile.intent.value
            intents[intent_key] = intents.get(intent_key, 0) + 1

            privacy_key = profile.privacy.value
            privacy_levels[privacy_key] = privacy_levels.get(privacy_key, 0) + 1

            total_confidence += profile.confidence

        avg_confidence = total_confidence / len(self.classification_history)

        return {
            "total_classified": len(self.classification_history),
            "intents": intents,
            "privacy_levels": privacy_levels,
            "avg_confidence": avg_confidence,
        }
