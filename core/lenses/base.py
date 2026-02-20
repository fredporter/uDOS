"""Lens base types and helpers."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class GameState:
    """Container output state for lens rendering."""

    variant: str
    raw_output: str
    viewport_width: int
    viewport_height: int
    status_line: Optional[str] = None
    message_queue: Optional[List[str]] = None
    input_ready: bool = True


@dataclass
class LensOutput:
    """Rendered viewport output."""

    view_name: str
    rendered_frame: str
    dimensions: Tuple[int, int]
    input_prompt: str
    metadata: Dict[str, Any]


class BaseLens:
    """Base lens with simple helpers."""

    name = "base"
    description = "Base lens"
    supported_variants: Tuple[str, ...] = tuple()

    def __init__(self, width: int = 80, height: int = 24) -> None:
        self.width = max(20, int(width))
        self.height = max(10, int(height))

    def supports_variant(self, variant: str) -> bool:
        if not self.supported_variants:
            return True
        return variant in self.supported_variants

    def render(self, state: GameState) -> LensOutput:
        raise NotImplementedError

    def translate_input(self, user_input: str) -> str:
        return user_input

    def get_metadata(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "description": self.description,
            "supported_variants": ",".join(self.supported_variants),
        }

    def _clamp_lines(self, lines: List[str]) -> List[str]:
        clamped = []
        for line in lines[: self.height]:
            if len(line) > self.width:
                clamped.append(line[: self.width])
            else:
                clamped.append(line.ljust(self.width))
        return clamped

    def _frame(self, title: str, body_lines: List[str]) -> str:
        width = self.width
        line = "-" * width
        head = title[:width]
        lines = [line, head, line]
        lines.extend(self._clamp_lines(body_lines))
        return "\n".join(lines[: self.height])
