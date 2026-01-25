"""
Wizard Dev TUI
==============

Dedicated Dev-only TUI for repair, backup, and recovery operations.
Assumes core/wizard may be unhealthy and runs diagnostics on startup.
"""

from __future__ import annotations

import os
import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
except Exception:
    PromptSession = None
    InMemoryHistory = None

from wizard.services.logging_manager import get_logger
from wizard.services.path_utils import get_repo_root
from wizard.services.repair_service import get_repair_service
from core.services.maintenance_utils import (
    create_backup,
    restore_backup,
    tidy,
    clean,
    compost,
    list_backups,
    default_repo_allowlist,
    default_memory_allowlist,
    get_memory_root,
)


@dataclass
class CommandResult:
    ok: bool
    message: str = ""


class WizardDevTUI:
    """Dev-only TUI for repair/backup/recovery workflows."""

    def __init__(self) -> None:
        self.logger = get_logger("wizard-dev-tui")
        self.repo_root = get_repo_root()
        self.repair_service = get_repair_service()
        self.running = False
        self.commands: Dict[str, Callable[[List[str]], CommandResult]] = {
            "HELP": self.cmd_help,
            "STATUS": self.cmd_status,
            "HEALTH": self.cmd_status,
            "REPAIR": self.cmd_repair,
            "BACKUP": self.cmd_backup,
            "RESTORE": self.cmd_restore,
            "TIDY": self.cmd_tidy,
            "CLEAN": self.cmd_clean,
            "COMPOST": self.cmd_compost,
            "DESTROY": self.cmd_destroy,
            "EXIT": self.cmd_exit,
            "QUIT": self.cmd_exit,
        }

    def run(self) -> None:
        self.running = True
        self._print_banner()
        self._print_diagnostics()

        if PromptSession is None:
            self._run_basic()
            return

        session = PromptSession(history=InMemoryHistory())
        while self.running:
            try:
                raw = session.prompt("dev> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not raw:
                continue
            self._dispatch(raw)

    def _run_basic(self) -> None:
        while self.running:
            try:
                raw = input("dev> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not raw:
                continue
            self._dispatch(raw)

    def _dispatch(self, raw: str) -> None:
        parts = raw.split()
        cmd = parts[0].upper()
        args = parts[1:]
        handler = self.commands.get(cmd)
        if not handler:
            print("Unknown command. Type HELP for list.")
            return
        result = handler(args)
        if result.message:
            print(result.message)

    def _print_banner(self) -> None:
        print("\n=== uDOS Wizard Dev TUI ===")
        print("Assumes core/wizard may be unhealthy. Use REPAIR to recover.\n")

    def _print_diagnostics(self) -> None:
        status = self.repair_service.status()
        os_info = status.get("os", {})
        tools = status.get("tools", {})
        print("Diagnostics:")
        print(f"  Repo: {self.repo_root}")
        print(f"  OS: {os_info.get('platform')} (alpine={os_info.get('is_alpine')})")
        tool_line = "  Tools: " + ", ".join(
            [f"{k}={'ok' if v.get('available') else 'missing'}" for k, v in tools.items()]
        )
        print(tool_line)
        print("  Use STATUS for full diagnostics.\n")

    def _parse_scope(self, args: List[str]) -> Tuple[str, List[str]]:
        if not args:
            return "workspace", []
        scope = args[0].lower()
        if scope in {"current", "+subfolders", "workspace", "all"}:
            return scope, args[1:]
        return "workspace", args

    def _resolve_scope(self, scope: str) -> Tuple[Path, bool]:
        if scope == "current":
            return Path.cwd(), False
        if scope == "+subfolders":
            return Path.cwd(), True
        if scope == "all":
            return self.repo_root, True
        return get_memory_root(), True

    def cmd_help(self, _args: List[str]) -> CommandResult:
        message = "\n".join(
            [
                "Commands:",
                "  STATUS/HEALTH        - Full diagnostics",
                "  REPAIR [subcmd]      - CHECK|BOOTSTRAP|PYTHON|DASH|BUILD|CLEAN|FULL",
                "  BACKUP [scope] [label]",
                "  RESTORE [scope] [--force]",
                "  TIDY [scope]         - Move junk into .archive",
                "  CLEAN [scope]        - Reset scope into .archive",
                "  COMPOST [scope]      - Move .archive/.backup/.tmp to /.compost",
                "  DESTROY CONFIRM      - Wipe and reinstall (requires confirmation)",
                "  EXIT/QUIT",
                "",
                "Scopes: current | +subfolders | workspace | all (default: workspace)",
            ]
        )
        return CommandResult(True, message)

    def cmd_status(self, _args: List[str]) -> CommandResult:
        status = self.repair_service.status()
        lines = ["\n=== STATUS ==="]
        os_info = status.get("os", {})
        lines.append(f"Repo: {self.repo_root}")
        lines.append(f"OS: {os_info.get('platform')} (alpine={os_info.get('is_alpine')})")
        lines.append("Tools:")
        for name, info in status.get("tools", {}).items():
            lines.append(f"  {name}: {'ok' if info.get('available') else 'missing'}")
        lines.append("Paths:")
        for key, info in status.get("paths", {}).items():
            lines.append(f"  {key}: {'ok' if info.get('exists') else 'missing'}")
        return CommandResult(True, "\n".join(lines))

    def cmd_repair(self, args: List[str]) -> CommandResult:
        action = args[0].lower() if args else "check"
        if action in {"check", "status"}:
            return self.cmd_status([])
        if action == "bootstrap":
            result = self.repair_service.bootstrap_venv()
            return CommandResult(result.success, result.output or result.message or result.error)
        if action == "python":
            result = self.repair_service.install_python_deps()
            return CommandResult(result.success, result.output or result.message or result.error)
        if action == "dash":
            result = self.repair_service.install_dashboard_deps()
            return CommandResult(result.success, result.output or result.message or result.error)
        if action == "build":
            result = self.repair_service.build_dashboard()
            return CommandResult(result.success, result.output or result.message or result.error)
        if action == "clean":
            moved = self._archive_artifacts()
            return CommandResult(True, f"Archived {moved} artifact paths into .archive")
        if action == "full":
            moved = self._archive_artifacts()
            boot = self.repair_service.bootstrap_venv()
            dash = self.repair_service.install_dashboard_deps()
            build = self.repair_service.build_dashboard()
            lines = [
                f"Archived: {moved}",
                boot.output or boot.message or boot.error,
                dash.output or dash.message or dash.error,
                build.output or build.message or build.error,
            ]
            return CommandResult(True, "\n".join([l for l in lines if l]))

        return CommandResult(False, "Unknown REPAIR action. Use REPAIR CHECK|BOOTSTRAP|PYTHON|DASH|BUILD|CLEAN|FULL")

    def _archive_artifacts(self) -> int:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        archive_root = self.repo_root / ".archive" / f"repair-{stamp}"
        archive_root.mkdir(parents=True, exist_ok=True)
        targets = [
            self.repo_root / ".venv",
            self.repo_root / "node_modules",
            self.repo_root / "wizard" / "dashboard" / "node_modules",
            self.repo_root / "wizard" / "dashboard" / "dist",
            self.repo_root / "wizard" / "dist",
        ]
        moved = 0
        for target in targets:
            if target.exists():
                dest = archive_root / target.name
                shutil.move(str(target), str(dest))
                moved += 1
        return moved

    def cmd_backup(self, args: List[str]) -> CommandResult:
        scope, remaining = self._parse_scope(args)
        label = "backup" if not remaining else " ".join(remaining)
        target_root, _recursive = self._resolve_scope(scope)
        archive_path, _manifest_path = create_backup(target_root, label)
        return CommandResult(True, f"Backup created: {archive_path}")

    def cmd_restore(self, args: List[str]) -> CommandResult:
        scope, remaining = self._parse_scope(args)
        target_root, _recursive = self._resolve_scope(scope)
        force = False
        if "--force" in remaining:
            force = True
            remaining = [p for p in remaining if p != "--force"]

        archive = None
        if remaining:
            candidate = Path(remaining[0])
            if candidate.exists():
                archive = candidate
        if archive is None:
            backups = list_backups(target_root)
            if not backups:
                return CommandResult(False, f"No backups found in {target_root / '.backup'}")
            archive = backups[0]

        try:
            message = restore_backup(archive, target_root, force=force)
            return CommandResult(True, message)
        except FileExistsError as exc:
            return CommandResult(False, f"{exc} (use RESTORE --force)")

    def cmd_tidy(self, args: List[str]) -> CommandResult:
        scope, _remaining = self._parse_scope(args)
        target_root, recursive = self._resolve_scope(scope)
        moved, archive_root = tidy(target_root, recursive=recursive)
        return CommandResult(True, f"Tidy complete. Moved {moved} -> {archive_root}")

    def cmd_clean(self, args: List[str]) -> CommandResult:
        scope, _remaining = self._parse_scope(args)
        target_root, recursive = self._resolve_scope(scope)
        if target_root == self.repo_root:
            allowlist = default_repo_allowlist()
        elif target_root == get_memory_root():
            allowlist = default_memory_allowlist()
        else:
            allowlist = []
        moved, archive_root = clean(
            target_root, allowed_entries=allowlist, recursive=recursive
        )
        return CommandResult(True, f"Clean complete. Moved {moved} -> {archive_root}")

    def cmd_compost(self, args: List[str]) -> CommandResult:
        scope, _remaining = self._parse_scope(args)
        target_root, recursive = self._resolve_scope(scope)
        moved, compost_root = compost(target_root, recursive=recursive)
        return CommandResult(True, f"Compost complete. Moved {moved} -> {compost_root}")

    def cmd_destroy(self, args: List[str]) -> CommandResult:
        if not args or (args[0].lower() not in {"confirm", "--confirm"}):
            return CommandResult(
                False,
                "DESTROY is destructive. Run: DESTROY CONFIRM",
            )
        return self._destroy_repo()

    def _destroy_repo(self) -> CommandResult:
        try:
            config_path = self.repo_root / "wizard" / "config" / "wizard.json"
            repo_slug = None
            if config_path.exists():
                data = json.loads(config_path.read_text())
                repo_slug = data.get("github_allowed_repo")

            backup = create_backup(self.repo_root, "destroy")
            parent = self.repo_root.parent
            compost_root = parent / ".compost"
            compost_root.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            moved_path = compost_root / f"uDOS-destroy-{stamp}"
            os.chdir(parent)
            shutil.move(str(self.repo_root), str(moved_path))

            if not repo_slug:
                return CommandResult(
                    True,
                    f"Moved repo to {moved_path}. No github repo configured to restore.",
                )

            git = shutil.which("git")
            if not git:
                return CommandResult(
                    True,
                    f"Moved repo to {moved_path}. Git not available to restore.",
                )

            clone_url = f"https://github.com/{repo_slug}.git"
            result = subprocess.run(
                [git, "clone", clone_url, str(self.repo_root)],
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode != 0:
                return CommandResult(
                    False,
                    f"Repo moved to {moved_path}, but clone failed: {result.stderr.strip()}",
                )
            return CommandResult(
                True,
                f"Repo moved to {moved_path} and re-cloned from {clone_url}",
            )
        except Exception as exc:
            return CommandResult(False, f"DESTROY failed: {exc}")

    def cmd_exit(self, _args: List[str]) -> CommandResult:
        self.running = False
        return CommandResult(True, "Exiting Dev TUI.")


def main() -> None:
    WizardDevTUI().run()


if __name__ == "__main__":
    main()
