"""OPERATOR command handler - dedicated alias for UCODE OPERATOR workflows."""

from __future__ import annotations

from typing import Any

from core.commands.base import BaseCommandHandler
from core.commands.ucode_handler import UcodeHandler


class OperatorHandler(BaseCommandHandler):
    """Handler for OPERATOR command - top-level operator planning and status."""

    def __init__(self) -> None:
        super().__init__()
        self.ucode_handler = UcodeHandler()

    def handle(
        self, command: str, params: list[str], grid: Any = None, parser: Any = None
    ) -> dict[str, Any]:
        return self.ucode_handler.handle("UCODE", ["OPERATOR", *params], grid, parser)
