"""
Vibe Dispatch Adapter for TUI

Integrates CommandDispatchService (three-stage dispatch + Vibe skill routing)
with the TUI's command handling pipeline.

This adapter bridges:
  - uCODE command matching (fuzzy, confidence scoring)
  - Shell command validation
  - Vibe skill routing (device, vault, workspace, etc.)
  - Fallback to OK (language model)

Integration point: core/tui/ucode.py::_route_input()
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import re

from core.services.command_dispatch_service import (
    CommandDispatchService,
    DispatchConfig,
    match_ucode_command,
    validate_shell_command,
    infer_vibe_skill,
)
from core.services.vibe_skill_mapper import (
    VibeSkillMapper,
    get_default_mapper,
)
from core.services.logging_manager import get_logger


@dataclass
class VibeDispatchResult:
    """Result of Vibe-integrated dispatch."""
    status: str  # "success", "error", "need_confirmation", "vibe_routed", "fallback_ok"
    command: Optional[str] = None
    skill: Optional[str] = None
    action: Optional[str] = None
    confidence: float = 0.0
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    validation_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for TUI handling."""
        if self.data is None:
            self.data = {}
        return {
            "status": self.status,
            "command": self.command,
            "skill": self.skill,
            "action": self.action,
            "confidence": self.confidence,
            "message": self.message,
            "validation_reason": self.validation_reason,
            "data": self.data,
        }


class VibeDispatchAdapter:
    """
    Adapter for integrating CommandDispatchService (three-stage) with TUI.

    Handles:
      1. uCODE command matching with confidence scoring
      2. Shell validation (safety checks)
      3. Vibe skill routing (natural language inference)
      4. Confidence-based confirmation for fuzzy matches
      5. OK fallback routing
    """

    def __init__(self):
        """Initialize the adapter."""
        self.logger = get_logger("vibe-dispatch-adapter")
        self.dispatcher = CommandDispatchService()
        self.skill_mapper = get_default_mapper()

    def dispatch(self, user_input: str, ask_confirm_fn=None) -> VibeDispatchResult:
        """
        Three-stage dispatch w/ Vibe skill routing.

        Args:
            user_input: Raw command string from user
            ask_confirm_fn: Optional function(question, default, help_text, variant) -> str
                           Returns "yes", "no", or "skip"

        Returns:
            VibeDispatchResult with status, command, skill, confidence, etc.
        """
        if not user_input or not user_input.strip():
            return VibeDispatchResult(
                status="error",
                message="Empty input",
            )

        user_input = user_input.strip()

        # Stage 1: Match uCODE Command (fuzzy, confidence scoring)
        cmd, confidence = match_ucode_command(user_input)

        self.logger.debug(
            f"[STAGE1] Matched command: {cmd}, confidence: {confidence:.2f}"
        )

        if cmd:
            # Handle confirmation for fuzzy matches
            if 0.80 <= confidence < 0.95 and ask_confirm_fn:
                choice = ask_confirm_fn(
                    question=f"Did you mean {cmd}?",
                    default=True,
                    help_text="Yes = run command, No = continue, Skip = try shell fallback",
                    variant="skip",
                )

                if choice == "yes":
                    return VibeDispatchResult(
                        status="success",
                        command=cmd,
                        confidence=confidence,
                        message=f"Executing {cmd} (fuzzy match)",
                    )
                elif choice == "skip":
                    self.logger.debug(f"[STAGE1] User skipped to fallback for: {cmd}")
                    return self._try_shell_or_fallback(user_input)
                else:
                    self.logger.debug(f"[STAGE1] User declined match, trying fallback")
                    return self._try_shell_or_fallback(user_input)

            elif confidence >= 0.95:
                # High confidence: execute directly
                return VibeDispatchResult(
                    status="success",
                    command=cmd,
                    confidence=confidence,
                    message=f"Executing {cmd}",
                )

        # No uCODE match: Try shell or Vibe skill
        return self._try_shell_or_fallback(user_input)

    def _try_shell_or_fallback(self, user_input: str) -> VibeDispatchResult:
        """
        Try shell command validation, then Vibe skill routing, then OK fallback.
        """
        # Stage 2: Shell Validation
        config = DispatchConfig()
        is_safe, validation_reason = validate_shell_command(user_input, config)

        self.logger.debug(
            f"[STAGE2] Shell validation: safe={is_safe}, reason={validation_reason}"
        )

        if is_safe:
            return VibeDispatchResult(
                status="success",
                message=f"Executing shell command: {user_input}",
                validation_reason="shell_valid",
                data={"shell_command": user_input},
            )

        # Stage 3: Vibe Skill Routing
        skill = infer_vibe_skill(user_input)

        self.logger.debug(f"[STAGE3] Vibe skill inference: {skill}")

        try:
            skill_contract = self.skill_mapper.get_skill(skill)
            if skill_contract:
                action = self._infer_skill_action(user_input, skill)
                return VibeDispatchResult(
                    status="vibe_routed",
                    skill=skill,
                    action=action,
                    message=f"Routed to Vibe skill '{skill}'",
                    data={
                        "skill_contract": skill_contract.to_dict() if hasattr(skill_contract, 'to_dict') else {},
                        "inferred_action": action,
                    },
                )
        except Exception as e:
            self.logger.warning(f"Failed to get skill {skill}: {e}")

        # Fallback: Route to OK (language model)
        self.logger.debug(f"[FALLBACK] Routing to OK for: {user_input}")

        return VibeDispatchResult(
            status="fallback_ok",
            message=f"Sending to language model",
            data={"ok_prompt": user_input},
        )

    def _infer_skill_action(self, user_input: str, skill: str) -> Optional[str]:
        """
        Infer which action within a skill is being requested.
        """
        lower = user_input.lower()

        skill_actions = {
            "device": {
                "list": [r"\b(list|show|all|devices)\b"],
                "status": [r"\b(status|health|check)\b"],
                "add": [r"\b(add|create|register)\b"],
                "update": [r"\b(update|modify|change)\b"],
            },
            "vault": {
                "list": [r"\b(list|show|keys)\b"],
                "get": [r"\b(get|retrieve|fetch|show)\b"],
                "set": [r"\b(set|store|save|put)\b"],
                "delete": [r"\b(delete|remove|clear)\b"],
            },
            "workspace": {
                "list": [r"\b(list|show|all)\b"],
                "switch": [r"\b(switch|change|select)\b"],
                "create": [r"\b(create|new|make)\b"],
                "delete": [r"\b(delete|remove)\b"],
            },
            "wizard": {
                "list": [r"\b(list|show|all)\b"],
                "start": [r"\b(start|run|execute)\b"],
                "stop": [r"\b(stop|halt|cancel)\b"],
                "status": [r"\b(status|check)\b"],
            },
            "network": {
                "scan": [r"\b(scan|check|discover)\b"],
                "connect": [r"\b(connect|link|join)\b"],
                "check": [r"\b(check|verify|test)\b"],
            },
            "script": {
                "list": [r"\b(list|show|all)\b"],
                "run": [r"\b(run|execute|play)\b"],
                "edit": [r"\b(edit|modify|change)\b"],
            },
            "user": {
                "list": [r"\b(list|show|all)\b"],
                "add": [r"\b(add|create|new)\b"],
                "remove": [r"\b(remove|delete)\b"],
                "update": [r"\b(update|modify)\b"],
            },
            "help": {
                "commands": [r"\b(commands|help|guide)\b"],
                "guide": [r"\b(guide|tutorial|learn)\b"],
            },
            "ask": {
                "query": [r".*"],
            },
        }

        actions = skill_actions.get(skill, {})

        for action, patterns in actions.items():
            for pattern in patterns:
                if re.search(pattern, lower):
                    return action

        return "query" if skill == "ask" else None


# Global Singleton
_adapter_instance: Optional[VibeDispatchAdapter] = None


def get_vibe_adapter() -> VibeDispatchAdapter:
    """Get or create the global Vibe dispatch adapter."""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = VibeDispatchAdapter()
    return _adapter_instance
