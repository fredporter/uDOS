"""Generic ASCII fallback lens."""

from typing import List

from core.lenses.base import BaseLens, GameState, LensOutput


class SimpleAsciiLens(BaseLens):
    """Generic grid-based lens for any variant."""

    name = "ascii"
    description = "Generic ASCII fallback lens"
    supported_variants = tuple()

    def render(self, state: GameState) -> LensOutput:
        raw_lines = (state.raw_output or "").splitlines()
        if not raw_lines:
            raw_lines = ["(no output)"]

        body_lines: List[str] = raw_lines[-self.height :]
        frame = self._frame("ASCII LENS", body_lines)
        prompt = "> " if state.input_ready else ""
        return LensOutput(
            view_name="ascii",
            rendered_frame=frame,
            dimensions=(self.width, self.height),
            input_prompt=prompt,
            metadata={"variant": state.variant},
        )
