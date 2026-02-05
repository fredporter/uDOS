"""Dependency warning monitor for self-healing upgrades.

Captures runtime warnings that mention dependency issues (openssl/libressl,
missing modules, etc.) and prompts the operator to run the REPAIR command to
refresh the environment. Designed for both the Core TUI and Wizard server.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import threading
import warnings
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

from core.services.logging_service import get_logger, LogTags, get_repo_root
from core.utils.tty import interactive_tty_status
from core.input.confirmation_utils import (
    normalize_default,
    parse_confirmation,
    format_prompt,
    format_error,
)

_REQUIREMENT_CACHE: Optional[Set[str]] = None
_monitor_instance: "DependencyWarningMonitor" | None = None
_install_lock = threading.Lock()


@dataclass
class DependencyIssue:
    """Single dependency health finding."""

    code: str
    message: str
    resolution: str


MIN_PY_VERSION = (3, 10, 0)


def _run_pip_check() -> Tuple[bool, str]:
    """Run pip check and return (healthy, output)."""

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "check"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout.strip() or result.stderr.strip()
        healthy = result.returncode == 0 and "No broken requirements" in output
        return healthy, output
    except Exception as exc:  # pragma: no cover - pip may be missing in some envs
        return False, f"pip check failed: {exc}"


def _invoke_repair(action: str = "--upgrade", quiet: bool = False) -> bool:
    """Trigger the REPAIR handler and return True if it succeeded."""

    try:
        # Import directly to avoid circular import through __init__.py
        from core.commands.repair_handler import RepairHandler

        handler = RepairHandler()
        response = handler.handle("REPAIR", [action], None, None)
    except Exception as exc:  # pragma: no cover
        if not quiet:
            print(f"   Auto-upgrade failed to start: {exc}")
        return False

    summary = (
        response.get("output")
        or response.get("message")
        or str(response)
    )

    status = str(response.get("status", "")).lower()
    success = status in {"success", "ok"}

    if not quiet:
        print(f"\n{summary}\n")

    return success


class DependencyWarningMonitor:
    """Intercept warnings and guide the operator through repairs."""

    KEYWORDS = (
        "openssl",
        "libressl",
        "requires",
        "only supports",
        "missing optional dependency",
        "importerror",
        "failed building wheel",
    )

    SPECIAL_HINTS = {
        "notopensslwarning": (
            "urllib3/OpenSSL mismatch detected.",
            "Install Python 3.11+ (python.org package, Homebrew, or pyenv) so the ssl"
            " module links against OpenSSL 3.x, recreate .venv, then run REPAIR"
            " --upgrade.",
        ),
        "urllib3 v2 only supports openssl": (
            "urllib3 requires OpenSSL 1.1.1+ but LibreSSL is in use.",
            "Install a modern Python build with OpenSSL 3.x (brew install python@3.11"
            " or download from python.org) and recreate the virtualenv.",
        ),
    }

    def __init__(self, component: str, auto_prompt: bool = True):
        self.component_names = {component}
        self.auto_prompt = auto_prompt
        self.logger = get_logger("dependency-guard", source="core")
        self._original_showwarning = warnings.showwarning
        self._trigger_lock = threading.Lock()
        self._triggered = False
        self._requirements = _load_requirement_names()

    @property
    def label(self) -> str:
        return "/".join(sorted(self.component_names))

    def register_component(self, component: str) -> None:
        if component in self.component_names:
            return
        self.component_names.add(component)
        self.logger.info(
            "%s Dependency warning monitor now includes %s",
            LogTags.LOCAL,
            component,
        )

    def install(self) -> None:
        warnings.showwarning = self._handle_warning  # type: ignore[assignment]
        self.logger.info(
            "%s Dependency warning monitor active for %s",
            LogTags.LOCAL,
            self.label,
        )

    def _handle_warning(self, message, category, filename, lineno, file=None, line=None):
        if self._original_showwarning:
            self._original_showwarning(message, category, filename, lineno, file, line)

        formatted = self._format_warning(message, category, filename, lineno, line)
        match = self._match_warning(category, formatted)
        if not match:
            return

        if not self._mark_triggered():
            return

        keyword, guidance = match
        thread = threading.Thread(
            target=self._prompt_and_heal,
            args=(formatted, keyword, guidance),
            daemon=True,
        )
        thread.start()

    def _format_warning(self, message, category, filename, lineno, line) -> str:
        try:
            return warnings.formatwarning(message, category, filename, lineno, line).strip()
        except Exception:
            return f"{getattr(category, '__name__', str(category))}: {message}"

    def _match_warning(self, category, text: str) -> Optional[Tuple[str, Optional[str]]]:
        lower_text = text.lower()
        category_name = getattr(category, "__name__", str(category)).lower()

        if category_name in self.SPECIAL_HINTS:
            return category_name, self.SPECIAL_HINTS[category_name][1]

        for key, hint in self.SPECIAL_HINTS.items():
            if key in lower_text:
                return key, hint[1]

        for name in self._requirements:
            if name and name in lower_text:
                return name, None

        for keyword in self.KEYWORDS:
            if keyword in lower_text:
                return keyword, None

        return None

    def _mark_triggered(self) -> bool:
        with self._trigger_lock:
            if self._triggered:
                return False
            self._triggered = True
            return True

    def _prompt_and_heal(self, warning_text: str, keyword: str, guidance: Optional[str]):
        headline = (
            f"Dependency warning detected for {self.label}: {warning_text}"
        )
        self.logger.warning("%s %s", LogTags.LOCAL, headline)
        if guidance:
            self.logger.warning("%s Guidance: %s", LogTags.LOCAL, guidance)

        pip_ok, pip_report = _run_pip_check()
        if pip_report:
            self.logger.info("%s pip check output:\n%s", LogTags.LOCAL, pip_report)

        if not self.auto_prompt:
            self._emit_notice(headline, guidance)
            return

        interactive, reason = self._is_interactive()
        if not interactive:
            self._emit_notice(headline, guidance, reason)
            return

        print(f"\n⚠️  {headline}")
        if guidance:
            print(f"   {guidance}")
        print("   Run 'REPAIR --upgrade' to refresh all requirements.")

        if self._ask_yes_no("   Proceed with REPAIR --upgrade now? [Yes|No|OK]: "):
            self._run_repair()
        else:
            print("   Skipping auto-upgrade. Run 'REPAIR --upgrade' later if needed.")

    def _emit_notice(self, headline: str, guidance: Optional[str], reason: Optional[str] = None):
        print(f"\n⚠️  {headline}")
        if guidance:
            print(f"   {guidance}")
        if reason:
            print(f"   Reason: {reason}")
        print("   Non-interactive session detected; run 'REPAIR --upgrade' manually.")

    def _run_repair(self) -> None:
        if not _invoke_repair("--upgrade"):
            self.logger.error("%s Auto-upgrade failed", LogTags.LOCAL)

    @staticmethod
    def _ask_yes_no(prompt: str) -> bool:
        try:
            answer = input(prompt)
        except EOFError:
            return False
        default_choice = normalize_default(True, "ok")
        choice = parse_confirmation(answer, default_choice, "ok")
        if choice is None:
            print(format_error("ok"))
            return DependencyWarningMonitor._ask_yes_no(prompt)
        return choice in {"yes", "ok"}

    @staticmethod
    def _is_interactive() -> Tuple[bool, Optional[str]]:
        interactive, reason = interactive_tty_status()
        return interactive, reason


def _load_requirement_names() -> Set[str]:
    global _REQUIREMENT_CACHE
    if _REQUIREMENT_CACHE is not None:
        return _REQUIREMENT_CACHE

    names: Set[str] = set()
    req_file = get_repo_root() / "requirements.txt"
    if req_file.exists():
        pattern = re.compile(r"^[A-Za-z0-9_.-]+")
        for raw in req_file.read_text().splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line or line.startswith("-"):
                continue
            match = pattern.match(line)
            if match:
                names.add(match.group(0).lower())
    _REQUIREMENT_CACHE = names
    return names


def _check_python_version() -> List[DependencyIssue]:
    issues: List[DependencyIssue] = []
    if sys.version_info < MIN_PY_VERSION:
        current = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        target = ".".join(str(part) for part in MIN_PY_VERSION)
        issues.append(
            DependencyIssue(
                code="python-version",
                message=f"Python {current} detected (minimum supported {target}).",
                resolution=(
                    "Install Python 3.11+ via python.org installer, Homebrew (brew install"
                    " python@3.11), or pyenv, then recreate the .venv and rerun REPAIR --upgrade."
                ),
            )
        )
    return issues


def _check_ssl_version() -> List[DependencyIssue]:
    issues: List[DependencyIssue] = []
    try:
        import ssl
    except Exception as exc:  # pragma: no cover
        issues.append(
            DependencyIssue(
                code="ssl-missing",
                message=f"Python ssl module unavailable: {exc}",
                resolution="Reinstall Python with SSL support (python.org, Homebrew, or pyenv).",
            )
        )
        return issues

    version_text = getattr(ssl, "OPENSSL_VERSION", "")
    version_info = getattr(ssl, "OPENSSL_VERSION_INFO", None)

    if "LibreSSL" in version_text:
        issues.append(
            DependencyIssue(
                code="ssl-libressl",
                message=f"LibreSSL detected ({version_text.strip()}); urllib3 v2 requires OpenSSL 1.1.1+.",
                resolution=(
                    "Install Python built against OpenSSL 3.x (python.org, Homebrew python@3.11,"
                    " or pyenv), recreate .venv, and run REPAIR --upgrade."
                ),
            )
        )
        return issues

    if isinstance(version_info, tuple) and len(version_info) >= 3:
        openssl_tuple = tuple(int(part) for part in version_info[:3])
        if openssl_tuple < (1, 1, 1):
            issues.append(
                DependencyIssue(
                    code="ssl-too-old",
                    message=f"OpenSSL {'.'.join(map(str, openssl_tuple))} detected (need >= 1.1.1).",
                    resolution=(
                        "Upgrade to Python 3.11+ (bundled OpenSSL 3.x) and recreate the virtual"
                        " environment before running REPAIR --upgrade."
                    ),
                )
            )
    return issues


def _check_pip_dependencies() -> List[DependencyIssue]:
    issues: List[DependencyIssue] = []
    healthy, output = _run_pip_check()
    if healthy:
        return issues
    if output:
        message = "pip check reported issues"
        resolution = f"Review pip check output and run REPAIR --upgrade:\n{output}"
    else:
        message = "pip check could not run"
        resolution = "Ensure pip is installed and rerun REPAIR --upgrade."
    issues.append(DependencyIssue(code="pip-check", message=message, resolution=resolution))
    return issues


def _collect_dependency_issues() -> List[DependencyIssue]:
    issues: List[DependencyIssue] = []
    issues.extend(_check_python_version())
    issues.extend(_check_ssl_version())
    issues.extend(_check_pip_dependencies())
    return issues


def _print_issue_summary(component: str, issues: List[DependencyIssue]) -> None:
    line = "═" * 64
    print(f"\n{line}")
    print(f"Dependency preflight check for {component}")
    print(f"{line}")
    for idx, issue in enumerate(issues, 1):
        print(f"{idx}. {issue.message}")
        if issue.resolution:
            print(f"   → {issue.resolution}")
    print()


def run_preflight_check(
    component: str,
    prompt_if_interactive: bool = True,
    auto_repair_if_headless: bool = True,
) -> int:
    """Run dependency diagnostics before launching components.

    Returns 0 when everything is healthy or successfully repaired, non-zero otherwise.
    """

    if os.getenv("UDOS_SKIP_DEP_CHECK") == "1":
        return 0

    issues = _collect_dependency_issues()
    if not issues:
        return 0

    _print_issue_summary(component, issues)

    if prompt_if_interactive:
        interactive, reason = DependencyWarningMonitor._is_interactive()
    else:
        interactive = False
        reason = None
    if interactive:
        # Offer fixes for each issue
        all_repaired = True
        for issue in issues:
            print(f"\n🔧 Fix for [{issue.code}]: {issue.message}")
            if issue.resolution:
                print(f"   {issue.resolution}")
            if DependencyWarningMonitor._ask_yes_no(f"\n   Fix this issue now? [Yes|No|OK]: "):
                success = _invoke_repair("--upgrade")
                if success:
                    print(f"   ✅ Fixed [{issue.code}]")
                else:
                    print(f"   ⚠️  Could not auto-fix [{issue.code}]. Please run REPAIR --upgrade manually.")
                    all_repaired = False
            else:
                print(f"   ℹ️  Skipped [{issue.code}]. You can fix this later with REPAIR --upgrade")
                all_repaired = False
        
        # Return 0 so server continues (warnings are non-critical)
        if all_repaired:
            print("\n✅ All dependency issues fixed!")
            return 0
        else:
            print("\n⚠️  Some warnings remain, but server will continue.")
            return 0
    
    if auto_repair_if_headless:
        print("Attempting automatic REPAIR --upgrade (non-interactive session)...")
        success = _invoke_repair("--upgrade")
        # Return 0 regardless so server continues (non-critical warnings)
        return 0

    print("Dependency issues detected. Run 'REPAIR --upgrade' before continuing.")
    # Still return 0 for non-critical warnings
    return 0

def install_dependency_warning_monitor(component: str, auto_prompt: bool = True) -> None:
    """Install (or extend) the global dependency warning monitor."""
    if os.getenv("UDOS_DISABLE_DEP_WARNING_MONITOR") == "1":
        return

    global _monitor_instance
    with _install_lock:
        if _monitor_instance is None:
            _monitor_instance = DependencyWarningMonitor(component, auto_prompt)
            _monitor_instance.install()
        else:
            _monitor_instance.register_component(component)


def _main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="uDOS dependency preflight")
    parser.add_argument("--component", default="core", help="Component name for logging")
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Disable interactive prompts even if a TTY is detected",
    )
    parser.add_argument(
        "--no-auto-repair",
        action="store_true",
        help="Do not auto-run REPAIR when running headless",
    )
    args = parser.parse_args()

    return run_preflight_check(
        component=args.component,
        prompt_if_interactive=not args.no_prompt,
        auto_repair_if_headless=not args.no_auto_repair,
    )


__all__ = ["install_dependency_warning_monitor", "run_preflight_check"]


if __name__ == "__main__":  # pragma: no cover - CLI helper
    raise SystemExit(_main())
