"""WEB command handler - URL fetching, web-to-Markdown conversion."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("command-web")


class WebHandler(BaseCommandHandler):
    """Handler for WEB command - fetch and convert web content.

    Commands:
      WEB                           — show help
      WEB FETCH <url>               — fetch URL and return raw HTML/text
      WEB MD <url> [--out <file>]   — convert URL to Markdown
      WEB SAVE <url> <file>         — save URL content to file
      WEB STATUS                    — check tool availability
    """

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return self._help()

        action = params[0].lower()

        if action in {"help", "?"}:
            return self._help()
        if action == "status":
            return self._status()
        if action == "fetch":
            return self._fetch(params[1:])
        if action in {"md", "markdown", "convert"}:
            return self._to_markdown(params[1:])
        if action == "save":
            return self._save(params[1:])

        # Treat bare URL as implicit fetch
        if params[0].startswith("http"):
            return self._fetch(params)

        return {"status": "error", "message": f"Unknown WEB action '{params[0]}'. Try WEB HELP."}

    # ------------------------------------------------------------------
    def _validate_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except Exception:
            return False

    def _status(self) -> Dict:
        curl_ok = shutil.which("curl") is not None
        pandoc_ok = shutil.which("pandoc") is not None
        # url-to-markdown library CLI
        utom_ok = shutil.which("url-to-markdown") is not None or shutil.which("utom") is not None
        return {
            "status": "success",
            "curl": curl_ok,
            "pandoc": pandoc_ok,
            "url_to_markdown_cli": utom_ok,
            "message": (
                "All web tools available" if (curl_ok and pandoc_ok)
                else "curl: " + ("ok" if curl_ok else "missing") + ", pandoc: " + ("ok" if pandoc_ok else "missing")
            ),
        }

    def _fetch(self, params: List[str]) -> Dict:
        if not params:
            return {"status": "error", "message": "Usage: WEB FETCH <url>"}
        url = params[0]
        if not self._validate_url(url):
            return {"status": "error", "message": f"Invalid URL: {url}"}
        if not shutil.which("curl"):
            return {"status": "error", "message": "curl not found in PATH."}
        try:
            result = subprocess.run(
                ["curl", "-sL", "--max-time", "30", url],
                capture_output=True, text=True, timeout=35,
            )
            if result.returncode != 0:
                return {"status": "error", "message": result.stderr.strip()[:200]}
            content = result.stdout
            return {"status": "success", "url": url, "length": len(content), "output": content[:2000]}
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Fetch timed out after 30s."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _to_markdown(self, params: List[str]) -> Dict:
        if not params:
            return {"status": "error", "message": "Usage: WEB MD <url> [--out <file>]"}

        url = None
        out_path = None
        i = 0
        while i < len(params):
            if params[i] in {"--out", "-o"} and i + 1 < len(params):
                out_path = params[i + 1]
                i += 2
            elif url is None:
                url = params[i]
                i += 1
            else:
                i += 1

        if not url or not self._validate_url(url):
            return {"status": "error", "message": f"Invalid URL: {url}"}

        logger.info(f"[WEB] to-markdown: {url}")

        # Try url-to-markdown CLI first
        for cli in ("url-to-markdown", "utom"):
            if shutil.which(cli):
                try:
                    result = subprocess.run(
                        [cli, url], capture_output=True, text=True, timeout=30,
                    )
                    if result.returncode == 0:
                        md = result.stdout.strip()
                        return self._save_or_return(md, out_path, url)
                except Exception:
                    pass

        # Fallback: curl + pandoc
        if not shutil.which("curl"):
            return {"status": "error", "message": "curl not found. Cannot fetch URL."}
        if not shutil.which("pandoc"):
            return {"status": "error", "message": "pandoc not found. Install pandoc for HTML→Markdown conversion."}

        try:
            curl = subprocess.run(
                ["curl", "-sL", "--max-time", "30", url],
                capture_output=True, text=True, timeout=35,
            )
            if curl.returncode != 0:
                return {"status": "error", "message": curl.stderr.strip()[:200]}

            pandoc = subprocess.run(
                ["pandoc", "-f", "html", "-t", "markdown", "--wrap=none"],
                input=curl.stdout, capture_output=True, text=True, timeout=15,
            )
            if pandoc.returncode != 0:
                return {"status": "error", "message": pandoc.stderr.strip()[:200]}

            md = pandoc.stdout.strip()
            return self._save_or_return(md, out_path, url)
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Conversion timed out."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _save_or_return(self, content: str, out_path: str | None, url: str) -> Dict:
        if out_path:
            p = Path(out_path)
            if not p.is_absolute():
                p = get_repo_root() / p
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
            return {"status": "success", "url": url, "saved_to": str(p), "length": len(content)}
        return {"status": "success", "url": url, "length": len(content), "output": content[:3000]}

    def _save(self, params: List[str]) -> Dict:
        if len(params) < 2:
            return {"status": "error", "message": "Usage: WEB SAVE <url> <file>"}
        url, out_path = params[0], params[1]
        if not self._validate_url(url):
            return {"status": "error", "message": f"Invalid URL: {url}"}
        if not shutil.which("curl"):
            return {"status": "error", "message": "curl not found in PATH."}
        p = Path(out_path)
        if not p.is_absolute():
            p = get_repo_root() / p
        p.parent.mkdir(parents=True, exist_ok=True)
        try:
            result = subprocess.run(
                ["curl", "-sL", "--max-time", "60", "-o", str(p), url],
                capture_output=True, text=True, timeout=65,
            )
            if result.returncode != 0:
                return {"status": "error", "message": result.stderr.strip()[:200]}
            return {"status": "success", "url": url, "saved_to": str(p), "size": p.stat().st_size}
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Download timed out after 60s."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _help(self) -> Dict:
        return {
            "status": "success",
            "output": (
                "WEB - URL fetch and Markdown conversion\n"
                "  WEB FETCH <url>                Fetch raw content\n"
                "  WEB MD <url> [--out <file>]    Convert URL to Markdown\n"
                "  WEB SAVE <url> <file>          Download URL to file\n"
                "  WEB STATUS                     Check tool availability\n"
            ),
        }
