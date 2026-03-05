"""
FILE Command Handler

Handles FILE command with workspace selection integration.
Provides interactive file browser with workspace picker.

Commands:
    FILE                    Open workspace picker then file browser
    FILE BROWSE             Same as FILE
    FILE NEW <name>         Create a new file in /memory
    FILE EDIT <path>        Open a file in editor
    FILE LIST [path]        List files (quick command, no picker)
    FILE SHOW <file>        Display file content

Part of Phase 2 TUI Enhancement — Workspace selection integration
"""

import shutil
import subprocess
import sys
from typing import Any, Dict, List
from pathlib import Path

from core.commands.base import BaseCommandHandler
from core.services.spatial_filesystem import UserRole
from core.tui.output import OutputToolkit


class FileHandler(BaseCommandHandler):
    """
    Handle FILE commands with workspace picker integration.

    Provides two modes:
    1. Interactive: FILE/FILE BROWSE opens WorkspacePicker → FileBrowser
    2. Quick: FILE LIST/SHOW for direct operations without picker
    """

    def __init__(self, file_editor: BaseCommandHandler = None):
        super().__init__()
        self.user_role = self._get_user_role()
        self._file_editor = file_editor

    def _get_user_role(self) -> UserRole:
        """Determine user role from state or config."""
        try:
            from core.services.user_service import get_user_manager, is_ghost_mode

            if is_ghost_mode():
                return UserRole.GUEST

            user = get_user_manager().current()
            if user and user.role:
                return UserRole(user.role.value)
        except Exception:
            pass

        admin_mode = self.get_state("dev_mode", False) or self.get_state("admin_mode", False)
        return UserRole.ADMIN if admin_mode else UserRole.USER

    def handle(
        self, command: str, params: List[str], grid=None, parser=None
    ) -> Dict[str, Any]:
        """
        Route FILE subcommands.

        Args:
            command: "FILE"
            params: Subcommand and parameters
            grid: TUI Grid (optional)
            parser: SmartPrompt parser (optional)

        Returns:
            Dict with status, message, output
        """
        if not params or params[0].upper() in ("BROWSE", "PICK", "OPEN"):
            return self._handle_interactive_browse()

        subcommand = params[0].upper()
        sub_params = params[1:] if len(params) > 1 else []

        match subcommand:
            case "NEW" | "EDIT":
                return self._handle_edit(subcommand, sub_params, grid, parser)
            case "LIST":
                return self._handle_list(sub_params)
            case "SHOW":
                return self._handle_show(sub_params)
            case "SELECT":
                return self._handle_select(sub_params)
            case "HELP":
                return self._handle_help()
            case _:
                return {
                    "status": "error",
                    "message": f"Unknown FILE subcommand: {subcommand}",
                    "suggestion": (
                        "Try: FILE, FILE SELECT, FILE NEW, FILE EDIT, "
                        "FILE LIST, FILE SHOW, FILE HELP"
                    ),
                }

    def _handle_edit(
        self,
        subcommand: str,
        params: List[str],
        grid=None,
        parser=None,
    ) -> Dict[str, Any]:
        if not self._file_editor:
            return {
                "status": "error",
                "message": "File editor not available",
            }
        return self._file_editor.handle(subcommand, params, grid, parser)

    def _handle_interactive_browse(self) -> Dict[str, Any]:
        """
        Launch interactive workspace picker followed by file browser.

        This is the main UX improvement from Phase 2: users pick a
        workspace first, then browse files within it.
        """
        try:
            from core.ui.workspace_selector import pick_workspace_then_file

            # Launch two-stage picker
            selected_file = pick_workspace_then_file(
                user_role=self.user_role,
                pick_directories=False,  # Files only
            )

            if selected_file is None:
                # User cancelled
                return {
                    "status": "cancelled",
                    "message": "File selection cancelled",
                }

            # File selected - show info
            output = "\n".join([
                OutputToolkit.banner("FILE BROWSER"),
                f"Selected: {selected_file}",
                f"Size: {selected_file.stat().st_size} bytes",
                "",
                "Use: FILE EDIT <file> to open in editor",
                "     PLACE READ @ws/file to read content",
            ])

            return {
                "status": "success",
                "message": "File selected",
                "output": output,
                "data": {"path": str(selected_file)},
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"File browser error: {e}",
            }

    def _handle_list(self, params: List[str]) -> Dict[str, Any]:
        """
        Quick file listing without picker.

        Args:
            params: [workspace_path] (optional)
        """
        try:
            from core.services.spatial_filesystem import SpatialFilesystem

            fs = SpatialFilesystem(user_role=self.user_role)

            # Default to @vault if no path provided
            workspace_ref = params[0] if params else "@vault"

            # List files
            locations = fs.list_workspace(workspace_ref)
            files = []
            for item in locations:
                size = item.absolute_path.stat().st_size if item.absolute_path.exists() else 0
                files.append(
                    {
                        "name": item.relative_path,
                        "size": size,
                        "is_dir": False,
                    }
                )

            # Format output
            lines = [
                OutputToolkit.banner(f"FILES: {workspace_ref}"),
                "",
            ]

            if not files:
                lines.append("  (empty)")
            else:
                for file_info in files:
                    name = file_info.get("name", "?")
                    size = file_info.get("size", 0)
                    is_dir = file_info.get("is_dir", False)
                    icon = "📁" if is_dir else "📄"
                    size_str = f"{size:,} bytes" if not is_dir else ""
                    lines.append(f"  {icon} {name:<40} {size_str}")

            lines.append("")
            lines.append(f"Total: {len(files)} items")

            return {
                "status": "success",
                "message": f"Listed {len(files)} files",
                "output": "\n".join(lines),
                "data": {"files": files, "workspace": workspace_ref},
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"List error: {e}",
            }

    def _handle_show(self, params: List[str]) -> Dict[str, Any]:
        """
        Display file content without picker.

        Args:
            params: [workspace_ref] (required)
        """
        if not params:
            return {
                "status": "error",
                "message": "FILE SHOW requires a file path",
                "suggestion": "Usage: FILE SHOW @vault/readme.md",
            }

        try:
            from core.services.spatial_filesystem import SpatialFilesystem

            fs = SpatialFilesystem(user_role=self.user_role)
            workspace_ref = params[0]

            # Read file
            content = fs.read_file(workspace_ref)

            # Format output
            lines = [
                OutputToolkit.banner(f"FILE: {workspace_ref}"),
                "",
                content,
                "",
                f"─" * 70,
                f"Lines: {len(content.splitlines())} | Chars: {len(content)}",
            ]

            return {
                "status": "success",
                "message": "File displayed",
                "output": "\n".join(lines),
                "data": {"path": workspace_ref, "content": content},
            }

        except FileNotFoundError:
            return {
                "status": "error",
                "message": f"File not found: {params[0]}",
            }
        except PermissionError as e:
            return {
                "status": "error",
                "message": f"Access denied: {e}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Read error: {e}",
            }

    def _is_interactive_terminal(self) -> bool:
        return sys.stdin.isatty() and sys.stdout.isatty()

    def _split_candidate_values(self, values: List[str]) -> List[str]:
        candidates: List[str] = []
        for value in values:
            for token in value.split(","):
                if cleaned := token.strip():
                    candidates.append(cleaned)
        return candidates

    def _parse_select_params(self, params: List[str]) -> Dict[str, Any]:
        workspace = "@vault"
        files: List[str] = []
        multi = True

        i = 0
        while i < len(params):
            token = params[i]
            match token:
                case "--workspace":
                    if i + 1 >= len(params):
                        raise ValueError("--workspace requires a value (example: @vault)")
                    workspace = params[i + 1]
                    i += 2
                case "--file":
                    if i + 1 >= len(params):
                        raise ValueError("--file requires a value")
                    files.append(params[i + 1])
                    i += 2
                case "--files":
                    i += 1
                    collected: List[str] = []
                    while i < len(params) and not params[i].startswith("--"):
                        collected.append(params[i])
                        i += 1
                    if not collected:
                        raise ValueError("--files requires one or more values")
                    files.extend(self._split_candidate_values(collected))
                case "--single":
                    multi = False
                    i += 1
                case _:
                    if token.startswith("--"):
                        raise ValueError(f"Unknown selector flag: {token}")
                    if token.startswith("@") and "/" not in token:
                        workspace = token
                    else:
                        files.append(token)
                    i += 1

        if not workspace.startswith("@"):
            workspace = f"@{workspace}"

        return {"workspace": workspace, "files": files, "multi": multi}

    def _as_workspace_ref(self, workspace: str, value: str) -> str:
        if value.startswith("@"):
            return value
        return f"{workspace.rstrip('/')}/{value.lstrip('/')}"

    def _validate_workspace_refs(self, fs: Any, refs: List[str]) -> Dict[str, Any] | None:
        missing: List[str] = []
        for ref in refs:
            try:
                fs.read_file(ref)
            except Exception:
                missing.append(ref)
        if not missing:
            return None
        return {
            "status": "error",
            "message": "One or more selected files do not exist",
            "missing": missing,
        }

    def _workspace_candidates(self, fs: Any, workspace: str) -> List[tuple[str, str, str]]:
        ws_type, _ = fs.resolve_workspace_reference(workspace)
        files = fs.list_workspace(workspace)
        return [
            (
                item.relative_path,
                f"@{ws_type.value}/{item.relative_path}",
                str(item.absolute_path),
            )
            for item in sorted(files, key=lambda x: x.relative_path)
        ]

    def _select_with_fzf(self, candidates: List[tuple[str, str, str]], multi: bool) -> List[str]:
        lines = [f"{label}\t{ref}\t{abs_path}" for label, ref, abs_path in candidates]
        args = [
            "fzf",
            "--delimiter",
            "\t",
            "--with-nth",
            "1",
            "--prompt",
            "Select files > ",
        ]
        if multi:
            args.append("--multi")
        if shutil.which("bat"):
            args.extend(["--preview", "bat --color=always {3}"])

        result = subprocess.run(
            args,
            input="\n".join(lines),
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode in {1, 130}:
            return []
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "fzf selection failed")

        selected: List[str] = []
        for row in result.stdout.splitlines():
            if len(parts := row.split("\t")) >= 2:
                selected.append(parts[1].strip())
        return selected

    def _select_with_gum(self, candidates: List[tuple[str, str, str]], multi: bool) -> List[str]:
        options = [ref for _, ref, _ in candidates]
        if not options:
            return []
        args = ["gum", "choose", "--header", "Select files"]
        if multi:
            args.append("--no-limit")
        args.extend(options)

        result = subprocess.run(args, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def _select_with_builtin_prompt(
        self,
        candidates: List[tuple[str, str, str]],
        multi: bool,
    ) -> List[str]:
        preview = candidates[:20]
        if not preview:
            return []

        print("Select files (comma-separated numbers, blank to cancel):")
        for idx, (label, ref, _) in enumerate(preview, start=1):
            print(f"  {idx:>2}. {label} ({ref})")

        raw = input("> ").strip()
        if not raw:
            return []

        selected: List[str] = []
        for token in raw.split(","):
            if not (cleaned := token.strip()).isdigit():
                continue
            pos = int(cleaned)
            if 1 <= pos <= len(preview):
                selected.append(preview[pos - 1][1])
                if not multi:
                    break
        return selected

    def _handle_select(self, params: List[str]) -> Dict[str, Any]:
        """
        Selector-enabled file selection for ucode.

        Supports:
        - FILE SELECT --file <path>
        - FILE SELECT --files <path1,path2>
        - FILE SELECT [--workspace @vault] [--single]
        """
        try:
            from core.services.spatial_filesystem import SpatialFilesystem

            parsed = self._parse_select_params(params)
            fs = SpatialFilesystem(user_role=self.user_role)
            workspace = parsed["workspace"]
            explicit_files = parsed["files"]
            multi = parsed["multi"]

            if explicit_files:
                refs = [self._as_workspace_ref(workspace, value) for value in explicit_files]
                if error := self._validate_workspace_refs(fs, refs):
                    return error
                return {
                    "status": "success",
                    "message": "File selection accepted (non-interactive)",
                    "selected_files": refs,
                    "data": {"selected_files": refs, "mode": "non-interactive"},
                }

            if not self._is_interactive_terminal():
                return {
                    "status": "error",
                    "message": "Non-interactive session: provide --file or --files",
                    "suggestion": "Example: FILE SELECT --files readme.md notes/todo.md",
                }

            candidates = self._workspace_candidates(fs, workspace)
            if not candidates:
                return {"status": "warning", "message": f"No files found in {workspace}"}

            if shutil.which("fzf"):
                selected = self._select_with_fzf(candidates, multi=multi)
                selector = "fzf"
            elif shutil.which("gum"):
                selected = self._select_with_gum(candidates, multi=multi)
                selector = "gum"
            else:
                selected = self._select_with_builtin_prompt(candidates, multi=multi)
                selector = "builtin"

            if not selected:
                return {"status": "cancelled", "message": "File selection cancelled"}

            return {
                "status": "success",
                "message": f"Selected {len(selected)} file(s) via {selector}",
                "selected_files": selected,
                "data": {
                    "selected_files": selected,
                    "mode": "interactive",
                    "selector": selector,
                },
            }
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Selector error: {e}"}

    def _handle_help(self) -> Dict[str, Any]:
        """Show FILE command help."""
        help_text = """
╭─────────────────────────────────────────────────────────────────╮
│  FILE COMMAND HELP                                              │
╰─────────────────────────────────────────────────────────────────╯

Interactive Mode:
  FILE                       Open workspace picker → file browser
  FILE BROWSE                Same as FILE
  FILE PICK                  Same as FILE
  FILE SELECT                Selector-enabled file picker (contributor-tool style)

Quick Commands:
    FILE NEW <name>               Create a new file in /memory
    FILE EDIT <path>              Open a file in editor
  FILE SELECT --file <path>   Non-interactive single file input
  FILE SELECT --files <paths> Non-interactive multi-file input
  FILE SELECT --workspace @ws  Interactive select in workspace
  FILE LIST [@workspace]     List files (default: @vault)
  FILE SHOW @ws/file.md      Display file content
  FILE HELP                  Show this help

Workspaces:
    @vault       Vault (default)
    @binders     Binder roots
    @inbox       Inbox intake
    @public      Public/open/published
    @submissions Submission intake
    @private     Private explicit share
    @shared      Shared space
    @knowledge   Knowledge base (admin only)
    @wizard      Wizard config (admin only)
    @dev         Development (admin only)

Examples:
  FILE                              # Open picker
  FILE SELECT                       # Interactive selector (TTY)
  FILE SELECT --files readme.md,todo.md
  FILE SELECT --workspace @vault --single
  FILE LIST @vault                  # List vault files
  FILE LIST @binders                # List binder roots
  FILE LIST @public                 # List public files
  FILE SHOW @vault/readme.md        # Show file content

Related Commands:
    FILE EDIT <file>                  # Open file in editor
    PLACE LIST @binders               # Spatial filesystem commands
    BINDER open @binders/project/sandbox # Open binder sandbox

Navigation in Picker:
  j/k or 2/8     Move down/up
  1-9            Quick select by number
  Enter or 5     Select item
  n/p or 0       Next/prev page
  q              Cancel/quit
  h/?            Help
""".strip()

        return {
            "status": "success",
            "message": "FILE command help",
            "output": help_text,
        }
