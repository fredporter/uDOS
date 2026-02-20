"""Crawler3D lens."""

from typing import List

from core.lenses.base import BaseLens, GameState, LensOutput


class Crawler3DLens(BaseLens):
    """Crawler3D first-person lens."""

    name = "crawler3d"
    description = "Crawler3D corridor lens"
    supported_variants = ("crawler3d",)

    def render(self, state: GameState) -> LensOutput:
        raw_lines = (state.raw_output or "").splitlines()
        if not raw_lines:
            raw_lines = ["(no crawler output)"]

        body_lines: List[str] = raw_lines[-self.height :]
        frame = self._frame("CRAWLER3D LENS", body_lines)
        prompt = "> " if state.input_ready else ""
        return LensOutput(
            view_name="crawler3d",
            rendered_frame=frame,
            dimensions=(self.width, self.height),
            input_prompt=prompt,
            metadata={"variant": state.variant},
        )
