"""Nethack-style lens."""

from typing import List

from core.lenses.base import BaseLens, GameState, LensOutput


class NethackLens(BaseLens):
    """Nethack dungeon lens."""

    name = "nethack"
    description = "Nethack dungeon lens"
    supported_variants = ("hethack", "nethack")

    def render(self, state: GameState) -> LensOutput:
        raw_lines = (state.raw_output or "").splitlines()
        if not raw_lines:
            raw_lines = ["(no dungeon output)"]

        body_lines: List[str] = raw_lines[-self.height :]
        frame = self._frame("NETHACK LENS", body_lines)
        prompt = "> " if state.input_ready else ""
        return LensOutput(
            view_name="nethack",
            rendered_frame=frame,
            dimensions=(self.width, self.height),
            input_prompt=prompt,
            metadata={"variant": state.variant},
        )
