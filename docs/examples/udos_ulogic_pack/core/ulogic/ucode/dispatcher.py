from __future__ import annotations
from pathlib import Path
from ..engine.contracts import ActorContext

class UcodeDispatcher:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def run(self, cmd: str, actor: ActorContext) -> str:
        # TODO: wire to uDOS CommandDispatcher
        return f"[UCODE STUB] role={actor.role} cmd={cmd}\n"
