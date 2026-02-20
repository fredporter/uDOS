"""RPGBBS lens."""

from typing import List

from core.lenses.base import BaseLens, GameState, LensOutput


class RPGBBSLens(BaseLens):
    """BBS-style RPG lens."""

    name = "rpgbbs"
    description = "BBS-style RPG lens"
    supported_variants = ("rpgbbs",)

    def render(self, state: GameState) -> LensOutput:
        raw_lines = (state.raw_output or "").splitlines()
        if not raw_lines:
            raw_lines = ["(no BBS output)"]

        body_lines: List[str] = raw_lines[-self.height :]
        frame = self._frame("RPGBBS LENS", body_lines)
        prompt = "> " if state.input_ready else ""
        return LensOutput(
            view_name="rpgbbs",
            rendered_frame=frame,
            dimensions=(self.width, self.height),
            input_prompt=prompt,
            metadata={"variant": state.variant},
        )
