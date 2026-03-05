"""
Dev Mode tool dispatch adapter for TUI

Integrates CommandDispatchService (three-stage dispatch + Dev Mode tool routing)
with the TUI's command handling pipeline.

This adapter bridges:
  - uCODE command matching (fuzzy, confidence scoring)
  - Shell command validation
  - Dev Mode contributor tool routing (device, vault, workspace, etc.)
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
    infer_dev_tool_skill,
)
from core.services.vibe_skill_mapper import get_default_mapper
from core.services.mode_policy import user_mode_scope_flag
from core.services.logging_manager import get_logger


@dataclass
class DevModeToolDispatchResult:
    """Result of Dev Mode contributor-tool-integrated dispatch."""
    status: str  # "success", "error", "need_confirmation", "dev_tool_routed", "fallback_ok"
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


class DevModeToolDispatchAdapter:
    """
    Adapter for integrating CommandDispatchService (three-stage) with TUI.

    Handles:
      1. uCODE command matching with confidence scoring
      2. Shell validation (safety checks)
      3. Dev Mode contributor tool routing (natural language inference)
      4. Confidence-based confirmation for fuzzy matches
      5. OK fallback routing
    """

    def __init__(self):
        """Initialize the adapter."""
        self.logger = get_logger("dev-mode-tool-dispatch-adapter")
        self.dispatcher = CommandDispatchService()
        self.skill_mapper = get_default_mapper()

    def dispatch(
        self,
        user_input: str,
        ask_confirm_fn=None,
        *,
        allow_skill_routing: bool = True,
        allow_model_fallback: bool = True,
    ) -> DevModeToolDispatchResult:
        """
        Three-stage dispatch w/ Dev Mode contributor tool routing.

        Args:
            user_input: Raw command string from user
            ask_confirm_fn: Optional function(question, default, help_text, variant) -> str
                           Returns "yes", "no", or "skip"

        Returns:
            DevModeToolDispatchResult with status, command, skill, confidence, etc.
        """
        if not user_input or not user_input.strip():
            return DevModeToolDispatchResult(
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
                    return DevModeToolDispatchResult(
                        status="success",
                        command=cmd,
                        confidence=confidence,
                        message=f"Executing {cmd} (fuzzy match)",
                    )
                elif choice == "skip":
                    self.logger.debug(f"[STAGE1] User skipped to fallback for: {cmd}")
                    return self._try_shell_or_fallback(
                        user_input,
                        allow_skill_routing=allow_skill_routing,
                        allow_model_fallback=allow_model_fallback,
                    )
                else:
                    self.logger.debug(f"[STAGE1] User declined match, trying fallback")
                    return self._try_shell_or_fallback(
                        user_input,
                        allow_skill_routing=allow_skill_routing,
                        allow_model_fallback=allow_model_fallback,
                    )

            elif confidence >= 0.95:
                # High confidence: execute directly
                return DevModeToolDispatchResult(
                    status="success",
                    command=cmd,
                    confidence=confidence,
                    message=f"Executing {cmd}",
                )

        # No uCODE match: Try shell or Dev Mode tool skill
        return self._try_shell_or_fallback(
            user_input,
            allow_skill_routing=allow_skill_routing,
            allow_model_fallback=allow_model_fallback,
        )

    def _try_shell_or_fallback(
        self,
        user_input: str,
        *,
        allow_skill_routing: bool,
        allow_model_fallback: bool,
    ) -> DevModeToolDispatchResult:
        """
        Try shell command validation, then Dev Mode contributor tool routing, then OK fallback.
        """
        policy_flag = user_mode_scope_flag(user_input)

        # Stage 2: Shell Validation
        config = DispatchConfig()
        is_safe, validation_reason = validate_shell_command(user_input, config)

        self.logger.debug(
            f"[STAGE2] Shell validation: safe={is_safe}, reason={validation_reason}"
        )

        if is_safe:
            data = {"shell_command": user_input}
            if policy_flag:
                data["policy_flag"] = policy_flag
            return DevModeToolDispatchResult(
                status="success",
                message=f"Executing shell command: {user_input}",
                validation_reason="shell_valid",
                data=data,
            )

        # Stage 3: Dev Mode contributor tool routing
        if allow_skill_routing:
            skill = infer_dev_tool_skill(user_input)

            self.logger.debug(f"[STAGE3] Dev Mode tool skill inference: {skill}")

            try:
                skill_contract = self.skill_mapper.get_skill(skill)
                if skill_contract:
                    action = self._infer_skill_action(user_input, skill)
                    return DevModeToolDispatchResult(
                        status="dev_tool_routed",
                        skill=skill,
                        action=action,
                        message=f"Routed to Dev Mode tool skill '{skill}'",
                        data={
                            "skill_contract": skill_contract.to_dict() if hasattr(skill_contract, 'to_dict') else {},
                            "inferred_action": action,
                            **({"policy_flag": policy_flag} if policy_flag else {}),
                        },
                    )
            except Exception as e:
                self.logger.warning(f"Failed to get skill {skill}: {e}")

        if not allow_model_fallback:
            return DevModeToolDispatchResult(
                status="fallback_local",
                message="Routing to local operator mode",
                data={
                    "operator_prompt": user_input,
                    **({"policy_flag": policy_flag} if policy_flag else {}),
                },
            )

        # Fallback: Route to OK (language model)
        self.logger.debug(f"[FALLBACK] Routing to OK for: {user_input}")

        return DevModeToolDispatchResult(
            status="fallback_ok",
            message=f"Sending to language model",
            data={
                "ok_prompt": user_input,
                **({"policy_flag": policy_flag} if policy_flag else {}),
            },
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
            "wizops": {
                "list": [r"\b(list|show|all)\b"],
                "start": [r"\b(start|run|execute)\b"],
                "stop": [r"\b(stop|halt|cancel)\b"],
                "status": [r"\b(status|check)\b"],
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
VibeDispatchResult = DevModeToolDispatchResult
VibeDispatchAdapter = DevModeToolDispatchAdapter

_adapter_instance: Optional[DevModeToolDispatchAdapter] = None


def get_vibe_adapter() -> DevModeToolDispatchAdapter:
    """Get or create the global Dev Mode tool dispatch adapter."""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = DevModeToolDispatchAdapter()
    return _adapter_instance
