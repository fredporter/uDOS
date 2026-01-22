"""
Mistral API + Vibe CLI Integration for Wizard Server
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from wizard.services.logging_manager import get_logger
from wizard.services.path_utils import get_repo_root

logger = get_logger("wizard.mistral-vibe")


class MistralVibeIntegration:
    """Mistral API + Vibe CLI integration."""

    def __init__(
        self,
        repo_path: str = None,
        vibe_config_path: Optional[str] = None,
        mistral_api_key: Optional[str] = None,
    ):
        self.repo_path = Path(repo_path or get_repo_root()).absolute()
        self.vibe_config = Path(vibe_config_path) if vibe_config_path else None
        self.mistral_api_key = mistral_api_key
        self._check_vibe_cli()

    def _check_vibe_cli(self) -> None:
        try:
            subprocess.run(["vibe", "--version"], capture_output=True, check=True)
        except FileNotFoundError:
            raise RuntimeError(
                "Vibe CLI not installed. See: https://mistral.ai/news/vibe/"
            )

    def get_context_files(self) -> Dict[str, str]:
        context: Dict[str, str] = {}
        files_to_read = [
            "AGENTS.md",
            "docs/roadmap.md",
            "docs/_index.md",
            ".github/copilot-instructions.md",
        ]
        for file_path in files_to_read:
            full_path = self.repo_path / file_path
            if full_path.exists():
                context[file_path] = full_path.read_text()

        devlog_dir = self.repo_path / "docs" / "devlog"
        if devlog_dir.exists():
            current_month = datetime.now().strftime("%Y-%m")
            devlog_path = devlog_dir / f"{current_month}.md"
            if devlog_path.exists():
                context[f"docs/devlog/{current_month}.md"] = devlog_path.read_text()

        log_dir = self.repo_path / "memory" / "logs"
        if log_dir.exists():
            today = datetime.now().strftime("%Y-%m-%d")
            for log_type in ["debug", "error", "session-commands"]:
                log_path = log_dir / f"{log_type}-{today}.log"
                if log_path.exists():
                    result = subprocess.run(
                        ["tail", "-n", "100", str(log_path)],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    context[f"logs/{log_type}-{today}.log"] = result.stdout

        return context

    def query_vibe(
        self, prompt: str, include_context: bool = True, model: str = "devstral-small"
    ) -> str:
        context_str = ""
        if include_context:
            context_files = self.get_context_files()
            context_str = "\n\n".join(
                [
                    f"=== {name} ===\n{content}"
                    for name, content in context_files.items()
                ]
            )

        full_prompt = f"""You are helping with the uDOS project.

Here is the current project context:

{context_str}

User request: {prompt}
"""
        result = subprocess.run(
            ["vibe", "chat", "--model", model],
            input=full_prompt,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def analyze_logs(self, log_type: str = "error") -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = self.repo_path / "memory" / "logs" / f"{log_type}-{today}.log"
        if not log_path.exists():
            return f"No {log_type} log found for {today}"
        result = subprocess.run(
            ["tail", "-n", "200", str(log_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        log_content = result.stdout
        prompt = f"""Analyze these recent {log_type} log entries and identify:
1. Critical issues
2. Patterns or recurring problems
3. Suggested fixes

Log entries:
{log_content}
"""
        return self.query_vibe(prompt, include_context=False)

    def suggest_next_steps(self) -> str:
        prompt = """Based on the current roadmap, recent devlog entries, and any error logs,
suggest the next 3-5 development tasks that should be prioritized.
"""
        return self.query_vibe(prompt, include_context=True)

    def explain_code(self, file_path: str, line_range: Optional[tuple] = None) -> str:
        full_path = self.repo_path / file_path
        if not full_path.exists():
            return f"File not found: {file_path}"
        content = full_path.read_text()
        if line_range:
            start, end = line_range
            lines = content.split("\n")
            content = "\n".join(lines[start - 1 : end])
        prompt = f"""Explain this code from {file_path}:

```
{content}
```

Provide:
1. High-level purpose
2. Key implementation details
3. Dependencies and integration points
"""
        return self.query_vibe(prompt, include_context=True)
