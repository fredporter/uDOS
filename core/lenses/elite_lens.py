"""Elite-style lens."""

from typing import List

from core.lenses.base import BaseLens, GameState, LensOutput


class EliteLens(BaseLens):
    """Elite galaxy corridor lens."""

    name = "elite"
    description = "Elite galaxy corridor lens"
    supported_variants = ("elite",)

    def render(self, state: GameState) -> LensOutput:
        raw_lines = (state.raw_output or "").splitlines()
        if not raw_lines:
            raw_lines = ["(no flight output)"]

        body_lines: List[str] = raw_lines[-self.height :]
        frame = self._frame("ELITE LENS", body_lines)
        prompt = "> " if state.input_ready else ""
        return LensOutput(
            view_name="elite",
            rendered_frame=frame,
            dimensions=(self.width, self.height),
            input_prompt=prompt,
            metadata={"variant": state.variant},
        )
