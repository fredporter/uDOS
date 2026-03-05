"""uDOS-owned interactive runtime helpers for routing and response handling."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
import re
from typing import Any

from core.services.command_dispatch_service import (
    DispatchConfig,
    match_ucode_command,
    validate_shell_command,
)
from core.services.logging_manager import get_logger


class RouteType(Enum):
    """Routing destination types for interactive input."""

    UCODE_COMMAND = auto()
    SHELL_COMMAND = auto()
    PROVIDER_FALLBACK = auto()
    SYNTAX_ERROR = auto()


@dataclass
class RouteDecision:
    """Result of routing a single input string."""

    route_type: RouteType
    command: str | None = None
    confidence: float = 0.0
    error: str | None = None
    metadata: dict[str, Any] | None = None


class InputRouter:
    """Route input to ucode, shell, or provider fallback."""

    def __init__(
        self, *, shell_enabled: bool = False, ucode_confidence_threshold: float = 0.80
    ) -> None:
        self.shell_enabled = shell_enabled
        self.ucode_threshold = ucode_confidence_threshold
        self.logger = get_logger("udos", category="router")
        self.dispatch_config = DispatchConfig(shell_enabled=shell_enabled)

    def route(self, user_input: str) -> RouteDecision:
        if not user_input or not user_input.strip():
            return RouteDecision(route_type=RouteType.SYNTAX_ERROR, error="Empty input")

        user_input = user_input.strip()
        command, confidence = match_ucode_command(user_input)
        if command and confidence >= self.ucode_threshold:
            return RouteDecision(
                route_type=RouteType.UCODE_COMMAND,
                command=command,
                confidence=confidence,
                metadata={"original_input": user_input},
            )

        if self.shell_enabled:
            is_safe, reason = validate_shell_command(user_input, self.dispatch_config)
            if is_safe:
                return RouteDecision(
                    route_type=RouteType.SHELL_COMMAND,
                    command=user_input,
                    metadata={"validation_reason": reason},
                )

        return RouteDecision(
            route_type=RouteType.PROVIDER_FALLBACK,
            metadata={"original_input": user_input},
        )


@dataclass
class ExecutionResult:
    """Result of executing a command."""

    status: str
    output: str | None = None
    message: str | None = None
    command: str | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None


class CommandEngine:
    """Execute ucode commands with deterministic short-circuit behavior."""

    def __init__(self) -> None:
        self.logger = get_logger("udos", category="command-engine")

    def execute_ucode(self, command: str, dispatcher: Any = None) -> ExecutionResult:
        if not command or not command.strip():
            return ExecutionResult(
                status="error",
                error="Empty command",
                message="Command cannot be empty",
            )

        command = command.strip()
        try:
            if dispatcher is None:
                from core.tui.dispatcher import CommandDispatcher

                dispatcher = CommandDispatcher()

            result = dispatcher.dispatch(command)
            output = (
                result.get("output")
                or result.get("rendered")
                or result.get("message")
                or ""
            )
            return ExecutionResult(
                status=result.get("status", "success"),
                output=output,
                command=command,
                message=result.get("message"),
                metadata={"dispatch_result": result},
            )
        except Exception as exc:
            self.logger.error(
                f"[CommandEngine] Execution failed: {exc}", extra={"command": command}
            )
            return ExecutionResult(
                status="error",
                error=str(exc),
                command=command,
                message=f"Command execution failed: {exc}",
            )


@dataclass
class NormalisedResponse:
    """Normalized provider response."""

    text: str
    contains_ucode: bool = False
    ucode_commands: list[str] | None = None
    is_safe: bool = True
    warnings: list[str] | None = None


class ResponseNormaliser:
    """Normalize response text before display or optional execution."""

    CODE_BLOCK_PATTERN = re.compile(
        r"```(?:ucode|bash|shell)?\n(.*?)\n```", re.DOTALL | re.IGNORECASE
    )
    DANGEROUS_PATTERNS = [
        r"\brm\s+-rf\s+/",
        r"\b:\(\)\s*\{",
        r">\s*/dev/sd[a-z]",
        r"\bcurl\s+.*\|\s*(?:bash|sh)",
        r"\bwget\s+.*\|\s*(?:bash|sh)",
    ]

    def __init__(self) -> None:
        self.logger = get_logger("udos", category="normaliser")

    def normalise(self, raw_response: str) -> NormalisedResponse:
        if not raw_response or not raw_response.strip():
            return NormalisedResponse(text="", is_safe=True)

        text = self._strip_markdown(raw_response)
        commands = self._extract_ucode_commands(text)
        is_safe, warnings = self._validate_safety(text)
        return NormalisedResponse(
            text=text.strip(),
            contains_ucode=bool(commands),
            ucode_commands=commands,
            is_safe=is_safe,
            warnings=warnings,
        )

    def _strip_markdown(self, text: str) -> str:
        matches = self.CODE_BLOCK_PATTERN.findall(text)
        if matches:
            text = matches[0]
        text = re.sub(r"`([^`]+)`", r"\1", text)
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
        return text.strip()

    def _extract_ucode_commands(self, text: str) -> list[str] | None:
        commands: list[str] = []
        for line in text.splitlines():
            candidate = line.strip()
            if not candidate:
                continue
            command, confidence = match_ucode_command(candidate)
            if command and confidence >= 0.80:
                commands.append(candidate)
        return commands or None

    def _validate_safety(self, text: str) -> tuple[bool, list[str] | None]:
        warnings: list[str] = []
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                warnings.append(f"Dangerous pattern detected: {pattern}")
        if re.search(r";\s*rm\b", text, re.IGNORECASE):
            warnings.append("Suspicious command chaining detected")
        if warnings:
            self.logger.warning(f"[Normaliser] Safety warnings: {', '.join(warnings)}")
        return (len(warnings) == 0, warnings or None)
