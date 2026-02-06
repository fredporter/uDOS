"""Theme validation + preview routes."""

import json
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from wizard.services.theme_validator import ThemePackValidator


def create_theme_routes(auth_guard=None) -> APIRouter:
    router = APIRouter()
    validator = ThemePackValidator()
    themes_root = validator.themes_root

    def _get_theme_dir(theme_name: str) -> Path:
        theme_dir = themes_root / theme_name
        if not theme_dir.exists():
            raise HTTPException(status_code=404, detail="theme not found")
        return theme_dir

    def _load_theme_meta(theme_dir: Path) -> Dict[str, Any]:
        json_path = theme_dir / "theme.json"
        if not json_path.exists():
            return {}
        try:
            return json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    @router.get("/api/theme/validate")
    async def validate_all():
        if auth_guard:
            await auth_guard()
        results = validator.validate_all()
        summary = validator.summarize(results)
        payload = {
            "summary": summary,
            "results": {
                name: {
                    "valid": res.valid,
                    "errors": res.errors,
                    "warnings": res.warnings,
                }
                for name, res in results.items()
            },
        }
        return payload

    @router.get("/api/theme/validate/{theme_name}")
    async def validate_theme(theme_name: str):
        if auth_guard:
            await auth_guard()
        results = validator.validate_all()
        if theme_name not in results:
            raise HTTPException(status_code=404, detail="theme not found")
        res = results[theme_name]
        return {
            "name": theme_name,
            "valid": res.valid,
            "errors": res.errors,
            "warnings": res.warnings,
        }

    @router.get("/api/theme/list")
    async def list_themes():
        if auth_guard:
            await auth_guard()
        results = validator.validate_all()
        summary = validator.summarize(results)
        items = []
        for name, res in results.items():
            items.append(
                {
                    "name": name,
                    "valid": res.valid,
                    "errors": res.errors,
                    "warnings": res.warnings,
                }
            )
        return {"summary": summary, "themes": items}

    @router.get("/api/theme/{theme_name}")
    async def get_theme(theme_name: str):
        if auth_guard:
            await auth_guard()
        theme_dir = _get_theme_dir(theme_name)
        meta = _load_theme_meta(theme_dir)
        return {"name": theme_name, "meta": meta}

    @router.get("/api/theme/assets/{theme_name}/{asset_path:path}")
    async def get_theme_asset(theme_name: str, asset_path: str):
        if auth_guard:
            await auth_guard()
        theme_dir = _get_theme_dir(theme_name)
        asset = (theme_dir / asset_path).resolve()
        if not str(asset).startswith(str(theme_dir.resolve())):
            raise HTTPException(status_code=403, detail="invalid asset path")
        if not asset.exists() or not asset.is_file():
            raise HTTPException(status_code=404, detail="asset not found")
        return FileResponse(str(asset))

    @router.get("/api/theme/preview/{theme_name}")
    async def preview_theme(theme_name: str):
        if auth_guard:
            await auth_guard()
        theme_dir = _get_theme_dir(theme_name)
        shell_path = theme_dir / "shell.html"
        if not shell_path.exists():
            raise HTTPException(status_code=404, detail="shell.html not found")

        shell = shell_path.read_text(encoding="utf-8", errors="ignore")
        sample = {
            "title": f"{theme_name} preview",
            "nav": "<nav><strong>uDOS</strong> · Theme Preview</nav>",
            "content": (
                "<h1>Theme Preview</h1>"
                "<p>This is a deterministic preview for the theme pack.</p>"
                "<ul><li>UGRID export</li><li>Vault render</li><li>Offline-first</li></ul>"
            ),
            "meta": "<!-- meta slot -->",
            "footer": "<small>uDOS · Theme Preview</small>",
        }

        html = shell
        for key, value in sample.items():
            html = html.replace(f"{{{{{key}}}}}", value)

        # Ensure relative asset paths resolve through API asset endpoint.
        html = html.replace(
            "href=\"theme.css\"",
            f"href=\"/api/theme/assets/{theme_name}/theme.css\"",
        )
        html = html.replace(
            "src=\"assets/",
            f"src=\"/api/theme/assets/{theme_name}/assets/",
        )
        html = html.replace(
            "href=\"assets/",
            f"href=\"/api/theme/assets/{theme_name}/assets/",
        )

        return HTMLResponse(content=html)

    return router
