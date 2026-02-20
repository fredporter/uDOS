"""
STORY command handler - parse and run -story.md files.

Story format is a sandboxed, interactive markdown format for:
- Setup wizards
- Data collection forms
- Interactive games
- Distributable questionnaires

Uses Core's TypeScript runtime for execution.
"""

from pathlib import Path
from typing import Dict, List, Optional

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_repo_root
from core.services.ts_runtime_service import TSRuntimeService
from core.tui.output import OutputToolkit


class StoryHandler(BaseCommandHandler):
    """Handler for STORY command - parse and execute story format files."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        STORY command dispatcher.

        Usage:
            STORY                    List all -story.md files
            STORY <file>             Run a story file
            STORY PARSE <file>       Parse and show structure
            STORY NEW <name>         Create new story template
        """
        if not params:
            return self._list_stories()

        subcommand = params[0].upper()

        if subcommand == "PARSE":
            if len(params) < 2:
                return {"status": "error", "message": "Usage: STORY PARSE <file>"}
            return self._parse_story(params[1])

        elif subcommand == "NEW":
            if len(params) < 2:
                return {"status": "error", "message": "Usage: STORY NEW <name>"}
            return self._create_story(params[1])

        else:
            # Assume first param is the file to run
            return self._run_story(params[0], section_id=params[1] if len(params) > 1 else None)

    def _list_stories(self) -> Dict:
        """List all -story.md files in memory/story/."""
        repo_root = get_repo_root()
        story_dir = repo_root / "memory" / "story"

        if not story_dir.exists():
            return {
                "status": "warning",
                "message": "No stories found",
                "output": "Directory memory/story/ does not exist.\nCreate one with: STORY NEW <name>",
            }

        story_files = list(story_dir.glob("*-story.md"))

        if not story_files:
            return {
                "status": "warning",
                "message": "No stories found",
                "output": "No -story.md files in memory/story/\nCreate one with: STORY NEW <name>",
            }

        # Build table
        rows = []
        for story_file in sorted(story_files):
            name = story_file.stem.replace("-story", "")
            size = story_file.stat().st_size
            modified = story_file.stat().st_mtime
            from datetime import datetime
            mod_str = datetime.fromtimestamp(modified).strftime("%Y-%m-%d")
            rows.append([name, f"{size} bytes", mod_str])

        output = OutputToolkit.table(["Story", "Size", "Modified"], rows)
        return {
            "status": "success",
            "message": f"Found {len(story_files)} stories",
            "output": output,
        }

    def _parse_story(self, file_arg: str) -> Dict:
        """Parse a story file and show structure."""
        script_path = self._resolve_path(file_arg)

        if not script_path.exists():
            return {
                "status": "error",
                "message": f"Story not found: {script_path}",
            }

        service = TSRuntimeService()
        result = service.parse(script_path)

        if result.get("status") != "success":
            return result

        payload = result.get("payload", {})
        frontmatter = payload.get("frontmatter", {})
        sections = payload.get("sections", [])

        # Build output
        lines = []
        lines.append(f"Story: {frontmatter.get('title', 'Untitled')}")
        lines.append(f"Format: {frontmatter.get('format', 'unknown')}")
        lines.append(f"Version: {frontmatter.get('version', 'unknown')}")
        lines.append("")
        lines.append(f"Sections: {len(sections)}")

        if sections:
            rows = []
            for section in sections:
                section_id = section.get("id", "")
                title = section.get("title", "")
                blocks = section.get("blocks", 0)
                rows.append([section_id, title, str(blocks)])

            lines.append("")
            lines.append(OutputToolkit.table(["ID", "Title", "Blocks"], rows))

        return {
            "status": "success",
            "message": "Story parsed",
            "output": "\n".join(lines),
            "frontmatter": frontmatter,
            "sections": sections,
        }

    def _run_story(self, file_arg: str, section_id: Optional[str] = None) -> Dict:
        """Execute a story file and return parsed structure."""
        script_path = self._resolve_path(file_arg)

        if not script_path.exists():
            return {
                "status": "error",
                "message": f"Story not found: {script_path}",
            }

        service = TSRuntimeService()
        # Call execute with no section_id to get all sections
        result = service.execute(script_path, section_id=None)

        if result.get("status") != "success":
            return result

        payload = result.get("payload", {})
        exec_result = payload.get("result", {})

        # Check if this returned all sections (multi-section form)
        if exec_result.get("allSections"):
            sections = exec_result.get("sections", [])
            # Check if any section has fields
            sections_with_fields = [s for s in sections if s.get("fields")]
            if sections_with_fields:
                return {
                    "status": "success",
                    "message": "Story form",
                    "story_form": {
                        "title": exec_result.get("frontmatter", {}).get("title", "Story"),
                        "sections": sections,
                        "text": "",
                    },
                    "output": f"Story form ready with {len(sections)} sections.",
                }

        # Single section or non-form
        fields = exec_result.get("fields", [])

        if fields:
            # Return structured form data for the TUI to handle interactively
            form_spec = {
                "title": exec_result.get("title", "Story Form"),
                "description": exec_result.get("text", "").strip(),
                "section_id": exec_result.get("sectionId"),
                "fields": fields,
            }

            # Process with interactive form handler
            form_result = self._process_interactive_form(form_spec)

            if form_result.get("status") == "success":
                return {
                    "status": "success",
                    "message": "Story form submitted",
                    "form_data": form_result.get("data", {}),
                    "output": "Form submitted successfully.",
                }
            else:
                return form_result

        else:
            # Non-form story - return output
            output = exec_result.get("output") or ""
            return {
                "status": "success",
                "message": "Story executed",
                "output": output,
                "runtime": payload,
            }

    def _create_story(self, name: str) -> Dict:
        """Create a new story template."""
        repo_root = get_repo_root()
        story_dir = repo_root / "memory" / "story"
        story_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize name
        safe_name = "".join(c for c in name if c.isalnum() or c in "-_")
        story_file = story_dir / f"{safe_name}-story.md"

        if story_file.exists():
            return {
                "status": "error",
                "message": f"Story already exists: {story_file.name}",
            }

        template = f"""---
title: {safe_name.replace("-", " ").title()}
format: story
version: 1.0.0
author: User
tags: [interactive, setup]
---

# Welcome

Welcome to your interactive story!

```state
$user = {{"name": "", "completed": false}}
```

## Introduction

This is a **story format** document. It's sandboxed and distributable.

Stories collect data and return results - perfect for:
- Setup wizards
- Data collection
- Interactive games
- Questionnaires

```form
name: "What is your name?"
  type: text
  required: true
```

## Next Steps

Thank you, $user.name!

You've completed the story.

```set
set $user.completed true
```

---

**Story created:** {story_file.name}
**Edit:** `FILE EDIT {story_file.relative_to(repo_root)}`
**Run:** `STORY {safe_name}`
"""

        story_file.write_text(template)

        return {
            "status": "success",
            "message": f"Story created: {story_file.name}",
            "output": f"Created: {story_file}\n\nRun with: STORY {safe_name}\nEdit with: FILE EDIT {story_file.relative_to(repo_root)}",
        }

    def _process_interactive_form(self, form_spec: Dict) -> Dict:
        """
        Process interactive form with TUI form handler.

        Args:
            form_spec: Form specification with title, description, fields

        Returns:
            Dictionary with status and collected data
        """
        try:
            from core.tui.story_form_handler import get_form_handler
            from core.services.logging_api import get_repo_root
            import os

            # Inject dynamic defaults for known setup fields.
            repo_root = get_repo_root()
            udos_root = os.getenv("UDOS_ROOT") or str(repo_root)
            vault_root = os.getenv("VAULT_ROOT") or str((repo_root / "memory" / "vault").resolve())
            fields = form_spec.get("fields", [])
            for field in fields:
                if field.get("name") == "setup_udos_root":
                    if not field.get("default"):
                        field["default"] = udos_root
                    if not field.get("placeholder"):
                        field["placeholder"] = udos_root
                if field.get("name") == "setup_vault_md_root":
                    if not field.get("default"):
                        field["default"] = vault_root
                    if not field.get("placeholder"):
                        field["placeholder"] = vault_root

            handler = get_form_handler()
            result = handler.process_story_form(form_spec)
            return result

        except Exception as e:
            from core.services.logging_api import get_logger
            logger = get_logger("story")
            logger.error(f"[LOCAL] Failed to process interactive form: {e}")

            # Fallback to basic message
            return {
                "status": "error",
                "message": f"Form processing failed: {e}",
            }

    def _resolve_path(self, file_arg: str) -> Path:
        """Resolve file path - check memory/story/, memory/bank/system/, core/framework/seed/bank/system/, then absolute."""
        repo_root = get_repo_root()

        # If no extension, assume -story.md
        if not file_arg.endswith(".md"):
            file_arg = f"{file_arg}-story.md"

        path = Path(file_arg)

        # If relative, check multiple locations
        if not path.is_absolute():
            # 1. Check memory/story/ first
            story_path = repo_root / "memory" / "story" / file_arg
            if story_path.exists():
                return story_path

            # 2. Check memory/bank/system/
            bank_system_path = repo_root / "memory" / "bank" / "system" / file_arg
            if bank_system_path.exists():
                return bank_system_path

            # 3. Check core/framework/seed/bank/system/
            core_seed_path = repo_root / "core" / "framework" / "seed" / "bank" / "system" / file_arg
            if core_seed_path.exists():
                return core_seed_path

            # Otherwise resolve from repo root
            return repo_root / path

        return path
