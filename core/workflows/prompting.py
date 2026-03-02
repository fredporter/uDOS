from __future__ import annotations

from pathlib import Path
import re


class PromptCompiler:
    def __init__(self, prompt_root: Path):
        self.prompt_root = prompt_root

    def load(self, adapter: str, prompt_name: str) -> str:
        path = self.prompt_root / adapter / "prompts" / f"{prompt_name}.md"
        if not path.exists():
            raise FileNotFoundError(f"Prompt not found: {path}")
        return path.read_text(encoding="utf-8")

    def compile(self, template: str, variables: dict[str, object]) -> str:
        def replace(match: re.Match[str]) -> str:
            key = match.group(1).strip()
            return str(variables.get(key, ""))

        return re.sub(r"\{\{\s*([^}]+)\s*\}\}", replace, template)
