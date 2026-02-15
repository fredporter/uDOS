"""Setup story loader for uCODE routes."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException


def load_setup_story() -> Dict[str, Any]:
    from core.services.story_service import parse_story_document
    from wizard.services.path_utils import get_memory_dir
    from wizard.services.path_utils import get_repo_root as wiz_repo_root

    repo_root = wiz_repo_root()
    template_candidates = [
        repo_root / "core" / "tui" / "setup-story.md",
        repo_root / "core" / "framework" / "seed" / "bank" / "system" / "tui-setup-story.md",
        repo_root / "wizard" / "templates" / "tui-setup-story.md",
    ]
    memory_root = get_memory_dir()
    story_dir = memory_root / "story"
    story_dir.mkdir(parents=True, exist_ok=True)
    story_path = story_dir / "tui-setup-story.md"
    if not story_path.exists():
        template_path = next((p for p in template_candidates if p.exists()), None)
        if not template_path:
            raise HTTPException(status_code=404, detail="Setup story template missing")
        story_path.write_text(template_path.read_text())

    raw_content = story_path.read_text()
    story_state = parse_story_document(
        raw_content,
        required_frontmatter_keys=["title", "type", "submit_endpoint"],
    )
    return story_state
