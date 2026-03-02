from __future__ import annotations

from pathlib import Path

from wizard.services.path_utils import get_vault_dir


class OpsWorkspaceService:
    def __init__(self, vault_root: Path | None = None):
        self.vault_root = vault_root or get_vault_dir()

    def list_sources(self, *, limit: int = 200) -> list[dict[str, str]]:
        patterns = ("tasks.md", "*.tasks.md", "*workflow*.md", "*schedule*.md")
        sources: list[dict[str, str]] = []
        for pattern in patterns:
            for path in sorted(self.vault_root.rglob(pattern)):
                rel = str(path.relative_to(self.vault_root))
                source_type = "task-list"
                lowered = path.name.lower()
                if "workflow" in lowered:
                    source_type = "workflow"
                elif "schedule" in lowered:
                    source_type = "schedule"
                sources.append({"path": rel, "type": source_type})
                if len(sources) >= limit:
                    return sources
        return sources
