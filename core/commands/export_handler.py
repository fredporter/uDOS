"""EXPORT command handler - Markdown-to-PDF and document export utilities."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_logger, get_repo_root
from core.services.error_contract import CommandError

logger = get_logger("command-export")


class ExportHandler(BaseCommandHandler):
    """Handler for EXPORT command - convert Markdown/docs to PDF and other formats.

    Commands:
      EXPORT                          — show help
      EXPORT PDF <file.md>            — convert Markdown to PDF
      EXPORT PDF <file.md> --out <f>  — specify output path
      EXPORT STATUS                   — check tool availability
      EXPORT FORMATS                  — list supported output formats
    """

    SUPPORTED_FORMATS = ("pdf", "html")

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return self._help()

        action = params[0].lower()

        if action in {"help", "?"}:
            return self._help()
        if action == "status":
            return self._status()
        if action == "formats":
            return {"status": "success", "formats": list(self.SUPPORTED_FORMATS), "output": "Supported: " + ", ".join(self.SUPPORTED_FORMATS)}
        if action == "pdf":
            return self._export_pdf(params[1:])
        if action == "html":
            return self._export_html(params[1:])

        # Treat as implicit PDF if first arg looks like a file
        if params[0].endswith(".md"):
            return self._export_pdf(params)

        raise CommandError(
            code="ERR_COMMAND_NOT_FOUND",
            message=f"Unknown EXPORT action '{params[0]}'. Try EXPORT HELP.",
            recovery_hint="Use EXPORT PDF, EXPORT HTML, or EXPORT HELP",
            level="INFO",
        )

    # ------------------------------------------------------------------
    def _resolve(self, path_str: str) -> Path:
        p = Path(path_str)
        if not p.is_absolute():
            p = get_repo_root() / p
        return p

    def _status(self) -> Dict:
        tools = {t: shutil.which(t) is not None for t in ("pandoc", "wkhtmltopdf", "chromium", "chromium-browser", "google-chrome")}
        pandoc_ok = tools.get("pandoc", False)
        chrome_ok = any(tools[k] for k in ("chromium", "chromium-browser", "google-chrome"))
        return {
            "status": "success",
            "pandoc": pandoc_ok,
            "chrome_headless": chrome_ok,
            "tools": tools,
            "message": (
                "pandoc available (PDF via LaTeX)" if pandoc_ok
                else "chromium available (PDF via headless print)" if chrome_ok
                else "No PDF converter found. Install pandoc or chromium."
            ),
        }

    def _parse_args(self, params: List[str]):
        """Parse params: <input_file> [--out <output>]."""
        out_path = None
        input_file = None
        i = 0
        while i < len(params):
            if params[i] in {"--out", "-o"} and i + 1 < len(params):
                out_path = params[i + 1]
                i += 2
            elif input_file is None:
                input_file = params[i]
                i += 1
            else:
                i += 1
        return input_file, out_path

    def _export_pdf(self, params: List[str]) -> Dict:
        if not params:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Usage: EXPORT PDF <file.md> [--out <output.pdf>]",
                recovery_hint="Provide input file path",
                level="INFO",
            )

        input_str, out_str = self._parse_args(params)
        if not input_str:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="No input file specified.",
                recovery_hint="Provide a Markdown file path",
                level="INFO",
            )

        src = self._resolve(input_str)
        if not src.exists():
            raise CommandError(
                code="ERR_IO_FILE_NOT_FOUND",
                message=f"File not found: {src}",
                recovery_hint="Check file path and try again",
                level="ERROR",
            )

        dest = Path(out_str) if out_str else src.with_suffix(".pdf")
        logger.info(f"[EXPORT] PDF: {src} -> {dest}")

        if shutil.which("pandoc"):
            cmd = ["pandoc", str(src), "-o", str(dest), "--pdf-engine=xelatex"]
        else:
            for chrome in ("chromium", "chromium-browser", "google-chrome"):
                if shutil.which(chrome):
                    cmd = [chrome, "--headless", "--disable-gpu", f"--print-to-pdf={dest}", str(src)]
                    break
            else:
                raise CommandError(
                    code="ERR_RUNTIME_DEPENDENCY_MISSING",
                    message="No PDF converter available. Install pandoc or chromium.",
                    recovery_hint="Install pandoc or chromium-browser",
                    level="ERROR",
                )

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                raise CommandError(
                    code="ERR_IO_WRITE_FAILED",
                    message=result.stderr.strip()[:300],
                    recovery_hint="Check input file and try again",
                    level="ERROR",
                )
            return {"status": "success", "output_path": str(dest), "message": f"PDF exported: {dest}"}
        except subprocess.TimeoutExpired:
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message="Export timed out after 60s.",
                recovery_hint="Try a smaller file or check system resources",
                level="ERROR",
            )
        except Exception as e:
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message=str(e),
                recovery_hint="Check file path and converter installation",
                level="ERROR",
                cause=e,
            )

    def _export_html(self, params: List[str]) -> Dict:
        if not params:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Usage: EXPORT HTML <file.md> [--out <output.html>]",
                recovery_hint="Provide input file path",
                level="INFO",
            )

        input_str, out_str = self._parse_args(params)
        if not input_str:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="No input file specified.",
                recovery_hint="Provide a Markdown file path",
                level="INFO",
            )

        src = self._resolve(input_str)
        if not src.exists():
            raise CommandError(
                code="ERR_IO_FILE_NOT_FOUND",
                message=f"File not found: {src}",
                recovery_hint="Check file path and try again",
                level="ERROR",
            )

        dest = Path(out_str) if out_str else src.with_suffix(".html")

        if not shutil.which("pandoc"):
            raise CommandError(
                code="ERR_RUNTIME_DEPENDENCY_MISSING",
                message="pandoc not found. Install pandoc for HTML export.",
                recovery_hint="Install pandoc",
                level="ERROR",
            )

        try:
            result = subprocess.run(
                ["pandoc", str(src), "-o", str(dest), "--standalone"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                raise CommandError(
                    code="ERR_IO_WRITE_FAILED",
                    message=result.stderr.strip()[:300],
                    recovery_hint="Check input file and try again",
                    level="ERROR",
                )
            return {"status": "success", "output_path": str(dest), "message": f"HTML exported: {dest}"}
        except Exception as e:
            raise CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message=str(e),
                recovery_hint="Check file path and converter installation",
                level="ERROR",
                cause=e,
            )

    def _help(self) -> Dict:
        return {
            "status": "success",
            "output": (
                "EXPORT - Document export utilities\n"
                "  EXPORT PDF <file.md> [--out <f>]   Convert Markdown to PDF\n"
                "  EXPORT HTML <file.md> [--out <f>]  Convert Markdown to HTML\n"
                "  EXPORT STATUS                       Check tool availability\n"
                "  EXPORT FORMATS                      List supported formats\n"
            ),
        }
