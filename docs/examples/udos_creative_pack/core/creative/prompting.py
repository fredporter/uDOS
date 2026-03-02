from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import re


class PromptCompiler:
    def __init__(self, prompt_root: Path):
        self.prompt_root = prompt_root

    def load(self, adapter: str, prompt_name: str) -> str:
        p = self.prompt_root / adapter / "prompts" / f"{prompt_name}.md"
        if not p.exists():
            raise FileNotFoundError(f"Prompt not found: {p}")
        return p.read_text(encoding="utf-8")

    def compile(self, template: str, vars: Dict[str, Any]) -> str:
        # Simple {{var}} substitution with safe stringification
        def repl(m):
            key = m.group(1).strip()
            return str(vars.get(key, ""))
        return re.sub(r"\{\{\s*([^}]+)\s*\}\}", repl, template)
