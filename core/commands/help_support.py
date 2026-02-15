"""Shared helpers for HELP command metadata, search, and text formatting."""

from __future__ import annotations

from typing import Any, Dict, List


def sync_with_registry(commands: Dict[str, Dict[str, Any]]) -> None:
    """Align HELP metadata with command registry metadata when available."""
    try:
        from core.input.command_prompt import create_default_registry

        registry = create_default_registry()
        for cmd in registry.list_all():
            name = cmd.name.upper()
            entry = commands.get(name)
            if entry is None:
                commands[name] = {
                    "description": cmd.help_text or f"{name} command",
                    "usage": cmd.syntax or name,
                    "example": cmd.examples[0] if cmd.examples else (cmd.syntax or name),
                    "notes": "Aligned from command registry metadata.",
                    "category": cmd.category or "General",
                    "syntax": cmd.syntax or name,
                }
                continue

            if cmd.syntax:
                entry["syntax"] = cmd.syntax
            if cmd.help_text and not entry.get("description"):
                entry["description"] = cmd.help_text
            if cmd.examples and not entry.get("example"):
                entry["example"] = cmd.examples[0]
            entry.setdefault("usage", entry.get("syntax", name))
            entry.setdefault("notes", "See command-specific docs for details.")
            entry.setdefault("category", cmd.category or "General")
    except Exception:
        return


def format_command_help(cmd_name: str, cmd_info: Dict[str, Any]) -> str:
    """Build detailed command help text."""
    return (
        f"HELP {cmd_name}\n"
        f"Category: {cmd_info.get('category', 'Uncategorized')}\n"
        f"Description: {cmd_info.get('description', '')}\n"
        f"Syntax: {cmd_info.get('syntax', cmd_info.get('usage', cmd_name))}\n"
        f"Usage: {cmd_info.get('usage', cmd_info.get('syntax', cmd_name))}\n"
        f"Example: {cmd_info.get('example', cmd_name)}\n"
        f"Notes: {cmd_info.get('notes', '')}\n"
    ).strip()


def format_syntax_help(cmd_name: str, cmd_info: Dict[str, Any]) -> str:
    """Build syntax-focused help text."""
    syntax = cmd_info.get("syntax", cmd_info.get("usage", cmd_name))
    return (
        f"HELP SYNTAX {cmd_name}\n"
        f"Syntax: {syntax}\n"
        f"Usage: {cmd_info.get('usage', syntax)}\n"
        f"Example: {cmd_info.get('example', cmd_name)}\n"
        f"Notes: {cmd_info.get('notes', '')}\n"
    ).strip()


def search_commands(commands: Dict[str, Dict[str, Any]], query: str) -> List[str]:
    """Return command ids matching a free-text query."""
    q = (query or "").strip().lower()
    if not q:
        return []

    matches: List[str] = []
    for cmd, info in commands.items():
        haystack = " ".join(
            [
                cmd,
                str(info.get("description", "")),
                str(info.get("syntax", "")),
                str(info.get("usage", "")),
                str(info.get("notes", "")),
            ]
        ).lower()
        if q in haystack:
            matches.append(cmd)
    return sorted(matches)


def format_search_results(
    query: str,
    matches: List[str],
    commands: Dict[str, Dict[str, Any]],
    limit: int = 20,
) -> str:
    """Build search output text block."""
    if not matches:
        return f"HELP SEARCH {query}\nNo matching commands."

    lines = [f"HELP SEARCH {query}", f"Matches: {len(matches)}", ""]
    for cmd in matches[:limit]:
        info = commands.get(cmd, {})
        lines.append(f"{cmd:<12} {info.get('description', '')}")
        lines.append(f"  Syntax: {info.get('syntax', info.get('usage', cmd))}")
    lines.append("")
    lines.append("Tip: use HELP DETAILED <command> for full details.")
    return "\n".join(lines).strip()
