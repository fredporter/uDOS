"""
Renderer Routes
===============

Expose metadata about theme packs, static exports, missions, and contributions so the portal
and SvelteKit admin lanes consume the same contracts described in `docs/Theme-Pack-Contract.md`
and `docs/Mission-Job-Schema.md`.
"""

import json
import os
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from wizard.services.contribution_service import ContributionService
from wizard.services.path_utils import get_repo_root
from wizard.services.permission_guard import require_role
from wizard.services.spatial_parser import scan_vault_places
from wizard.services.spatial_store import get_spatial_db_path, fetch_spatial_rows
from core.tools.contract_validator import (
    validate_theme_pack,
    validate_vault_contract,
    validate_world_contract,
)


def _themes_root() -> Path:
    env_root = os.getenv("THEMES_ROOT") or os.getenv("UDOS_THEMES_ROOT")
    if env_root:
        return Path(env_root)
    return get_repo_root() / "themes"


def _vault_root() -> Path:
    return get_repo_root() / "vault"


def _site_root() -> Path:
    return _vault_root() / "_site"


def _missions_root() -> Path:
    return _vault_root() / "06_RUNS"


def _contributions_root() -> Path:
    return _vault_root() / "contributions"


CONTRIBUTION_SERVICE = ContributionService(_vault_root())
CONTRIB_SUBMIT_GUARD = require_role("contributor", "editor", "maintainer")
CONTRIB_APPROVE_GUARD = require_role("maintainer")


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _datetime_from_stat(path: Path) -> Optional[str]:
    try:
        mtime = path.stat().st_mtime
        return datetime.utcfromtimestamp(mtime).isoformat() + "Z"
    except OSError:
        return None


def _site_stats(theme_name: str) -> Dict[str, Any]:
    site_dir = _site_root() / theme_name
    if not site_dir.exists():
        return {"files": 0, "totalSize": 0, "lastModified": None}
    file_count = 0
    total_size = 0
    last_modified: Optional[float] = None
    for path in site_dir.rglob("*"):
        if not path.is_file():
            continue
        file_count += 1
        try:
            size = path.stat().st_size
            total_size += size
            mtime = path.stat().st_mtime
            last_modified = max(last_modified or 0, mtime)
        except OSError:
            continue
    last_modified_iso = (
        datetime.utcfromtimestamp(last_modified).isoformat() + "Z"
        if last_modified
        else None
    )
    return {
        "files": file_count,
        "totalSize": total_size,
        "lastModified": last_modified_iso,
    }


def _list_site_files(theme_name: str) -> List[Dict[str, Any]]:
    site_dir = _site_root() / theme_name
    if not site_dir.exists():
        raise HTTPException(status_code=404, detail="Theme site not found")
    files: List[Dict[str, Any]] = []
    for path in sorted(site_dir.rglob("*.html")):
        files.append(
            {
                "path": path.relative_to(site_dir).as_posix(),
                "size": path.stat().st_size,
                "updatedAt": _datetime_from_stat(path),
            }
        )
    return files


def _collect_theme_metadata() -> List[Dict[str, Any]]:
    themes_dir = _themes_root()
    if not themes_dir.exists():
        return []
    metadata: List[Dict[str, Any]] = []
    for entry in sorted(themes_dir.iterdir()):
        if not entry.is_dir():
            continue
        meta = _load_json(entry / "theme.json")
        if not meta:
            continue
        meta["name"] = meta.get("name", entry.name)
        meta["siteExists"] = (_site_root() / entry.name).exists()
        meta["siteStats"] = _site_stats(entry.name)
        metadata.append(meta)
    return metadata


def _load_theme_metadata(theme_name: str) -> Dict[str, Any]:
    meta = _load_json(_themes_root() / theme_name / "theme.json")
    if not meta:
        raise HTTPException(status_code=404, detail="Theme not found or invalid JSON")
    meta["name"] = meta.get("name", theme_name)
    meta["siteExists"] = (_site_root() / theme_name).exists()
    meta["siteStats"] = _site_stats(theme_name)
    return meta


def _build_theme_preview_html(theme_name: str) -> str:
    theme_dir = _themes_root() / theme_name
    shell_path = theme_dir / "shell.html"
    css_path = theme_dir / "theme.css"
    if not shell_path.exists():
        raise HTTPException(status_code=404, detail="Theme shell not found")
    shell = shell_path.read_text(encoding="utf-8")
    css = ""
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")

    sample_title = f"{theme_name} Theme Preview"
    sample_nav = "<nav><a href=\"#\">Home</a> · <a href=\"#\">Docs</a> · <a href=\"#\">Notes</a></nav>"
    sample_meta = "<div class=\"meta\">Generated preview</div>"
    sample_footer = "<footer>uDOS · Theme preview</footer>"
    sample_content = """
<main>
  <h1>Theme Preview</h1>
  <p>This is a sample preview to validate slots, typography, and layout.</p>
  <h2>Sample Section</h2>
  <ul>
    <li>Bullet one</li>
    <li>Bullet two</li>
    <li>Bullet three</li>
  </ul>
  <pre><code>const demo = \"udos\";</code></pre>
</main>
""".strip()

    html = shell
    html = html.replace("{{title}}", sample_title)
    html = html.replace("{{content}}", sample_content)
    html = html.replace("{{nav}}", sample_nav)
    html = html.replace("{{meta}}", sample_meta)
    html = html.replace("{{footer}}", sample_footer)

    if css:
        if "</head>" in html:
            html = html.replace("</head>", f"<style>{css}</style></head>")
        else:
            html = f"<style>{css}</style>\n{html}"
    return html


def _validate_theme(theme_name: str) -> Dict[str, Any]:
    theme_dir = _themes_root() / theme_name
    report = validate_theme_pack(theme_dir)
    return {
        "theme": theme_name,
        "valid": report.valid,
        "errors": report.errors,
        "warnings": report.warnings,
        "details": report.details,
    }


def _collect_missions() -> List[Dict[str, Any]]:
    runs_root = _missions_root()
    missions: List[Dict[str, Any]] = []
    if not runs_root.exists():
        return missions
    for mission_dir in sorted(runs_root.iterdir()):
        if not mission_dir.is_dir():
            continue
        for file in sorted(mission_dir.glob("*.json")):
            content = _load_json(file)
            if not content:
                continue
            content["mission_id"] = content.get("mission_id", mission_dir.name)
            content["job_id"] = content.get("job_id", file.stem)
            missions.append(content)
    return missions


def _find_mission(mission_id: str) -> Optional[Dict[str, Any]]:
    missions = _collect_missions()
    for mission in missions:
        if mission.get("mission_id") == mission_id or mission.get("job_id") == mission_id:
            return mission
    return None


def _renderer_cli_path() -> Path:
    return get_repo_root() / "v1-3" / "core" / "dist" / "renderer" / "cli.js"


def _renderer_env() -> Dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "VAULT_ROOT": str(_vault_root()),
            "THEMES_ROOT": str(_themes_root()),
            "OUTPUT_ROOT": str(_site_root()),
        }
    )
    return env


def _invoke_renderer(theme: str, mission_id: Optional[str] = None) -> Dict[str, Any]:
    cli_path = _renderer_cli_path()
    if not cli_path.exists():
        raise HTTPException(
            status_code=500,
            detail="Renderer binary missing; run npm run build under v1-3/core.",
        )
    env = _renderer_env()
    env["THEME"] = theme
    if mission_id:
        env["MISSION_ID"] = mission_id

    started_at = datetime.utcnow().isoformat() + "Z"
    result = subprocess.run(
        ["node", str(cli_path)],
        capture_output=True,
        text=True,
        env=env,
    )

    if result.returncode != 0:
        # Write error report to 06_RUNS even on failure
        missionid = mission_id or f"renderer-{theme}"
        job_id = f"job-{uuid.uuid4()}"
        error_report = {
            "mission_id": missionid,
            "job_id": job_id,
            "status": "failed",
            "runner": "renderer-cli",
            "theme": theme,
            "started_at": started_at,
            "completed_at": datetime.utcnow().isoformat() + "Z",
            "error": result.stderr.strip(),
        }
        _write_mission_output(error_report)
        raise HTTPException(
            status_code=500,
            detail=f"Renderer failed: {result.stderr.strip()}",
        )
    try:
        result_payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500, detail="Renderer returned invalid JSON payload."
        )

    # Write success report to 06_RUNS
    result_payload["started_at"] = started_at
    result_payload["completed_at"] = datetime.utcnow().isoformat() + "Z"
    _write_mission_output(result_payload)

    return result_payload


def _write_mission_output(report: Dict[str, Any]) -> Optional[Path]:
    """Write mission output/report to vault/06_RUNS/<mission_id>/"""
    try:
        mission_id = report.get("mission_id", "unknown")
        job_id = report.get("job_id", f"job-{uuid.uuid4()}")
        runs_root = _missions_root()
        mission_dir = runs_root / mission_id
        mission_dir.mkdir(parents=True, exist_ok=True)
        report_path = mission_dir / f"{job_id}.json"
        report_path.write_text(json.dumps(report, indent=2))
        return report_path
    except Exception as e:
        import traceback
        print(f"[WARN] Failed to write mission output: {e}", file=sys.stderr)
        traceback.print_exc()
        return None


class ContributionSubmission(BaseModel):
    id: Optional[str]
    mission_id: Optional[str]
    notes: Optional[str]
    artifact: Optional[str]
    bundle: Optional[Dict[str, Any]]
    patch: Optional[str]


class ContributionStatusUpdate(BaseModel):
    status: str
    reviewer: Optional[str]
    note: Optional[str]


class RenderRequest(BaseModel):
    theme: Optional[str] = None
    mission_id: Optional[str] = None


def create_renderer_routes(auth_guard=None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/renderer", tags=["renderer"], dependencies=dependencies)

    @router.get("/themes")
    async def list_themes():
        return {"themes": _collect_theme_metadata()}

    @router.get("/themes/{theme_name}")
    async def get_theme(theme_name: str):
        return _load_theme_metadata(theme_name)

    @router.get("/themes/{theme_name}/preview", response_class=HTMLResponse)
    async def preview_theme(theme_name: str):
        html = _build_theme_preview_html(theme_name)
        return HTMLResponse(content=html)

    @router.post("/themes/{theme_name}/validate")
    async def validate_theme(theme_name: str):
        return _validate_theme(theme_name)

    @router.post("/themes/validate")
    async def validate_themes():
        results = []
        for entry in _collect_theme_metadata():
            name = entry.get("name")
            if not name:
                continue
            results.append(_validate_theme(name))
        return {"themes": results}

    @router.post("/contracts/validate")
    async def validate_contracts(payload: Optional[Dict[str, Any]] = Body(None)):
        theme_name = None
        if payload and isinstance(payload, dict):
            theme_name = payload.get("theme")
        theme_path = _themes_root() / (theme_name or "prose")
        vault_report = validate_vault_contract(_vault_root())
        theme_report = validate_theme_pack(theme_path)
        world_report = validate_world_contract(_vault_root())
        return {
            "vault": {
                "valid": vault_report.valid,
                "errors": vault_report.errors,
                "warnings": vault_report.warnings,
                "details": vault_report.details,
            },
            "theme": {
                "valid": theme_report.valid,
                "errors": theme_report.errors,
                "warnings": theme_report.warnings,
                "details": theme_report.details,
                "theme": theme_name or "prose",
            },
            "locid": {
                "valid": world_report.valid,
                "errors": world_report.errors,
                "warnings": world_report.warnings,
                "details": world_report.details,
            },
        }

    @router.get("/site")
    async def list_site_exports():
        summaries = []
        site_root = _site_root()
        for theme_path in sorted(site_root.iterdir()) if site_root.exists() else []:
            if theme_path.is_dir():
                stats = _site_stats(theme_path.name)
                summaries.append(
                    {
                        "theme": theme_path.name,
                        "files": stats["files"],
                        "lastModified": stats["lastModified"],
                    }
                )
        return {"exports": summaries}

    @router.get("/site/{theme_name}/files")
    async def site_files(theme_name: str):
        return {"theme": theme_name, "files": _list_site_files(theme_name)}

    @router.get("/missions")
    async def missions():
        return {"missions": _collect_missions()}

    @router.get("/missions/{mission_id}")
    async def mission_detail(mission_id: str):
        mission = _find_mission(mission_id)
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        return mission

    @router.get("/contributions")
    async def contributions(status: Optional[str] = Query(None)):
        if status and status not in ContributionService.STATUSES:
            raise HTTPException(status_code=400, detail="Unknown contribution status")
        return {"contributions": CONTRIBUTION_SERVICE.list(status)}

    @router.get("/contributions/{contribution_id}")
    async def contribution_detail(contribution_id: str):
        return {"contribution": CONTRIBUTION_SERVICE.get_entry(contribution_id)}

    @router.post(
        "/contributions",
        dependencies=[Depends(CONTRIB_SUBMIT_GUARD)],
    )
    async def submit_contribution(payload: ContributionSubmission):
        contribution = CONTRIBUTION_SERVICE.submit(payload.dict(exclude_none=True))
        return {"contribution": contribution}

    @router.post(
        "/contributions/{contribution_id}/status",
        dependencies=[Depends(CONTRIB_APPROVE_GUARD)],
    )
    async def update_contribution_status(
        contribution_id: str, payload: ContributionStatusUpdate
    ):
        contribution = CONTRIBUTION_SERVICE.update_status(
            contribution_id, payload.status, payload.reviewer, payload.note
        )
        return {"contribution": contribution}

    @router.get("/places")
    async def places():
        vault_root = _vault_root()
        places = scan_vault_places(vault_root)
        return {"places": places}

    @router.get("/spatial/anchors")
    async def spatial_anchors():
        db_path = get_spatial_db_path(create=True)
        if not db_path:
            raise HTTPException(status_code=404, detail="Spatial database not found")
        rows = fetch_spatial_rows(db_path, "SELECT * FROM anchors")
        return {"anchors": rows}

    @router.get("/spatial/places")
    async def spatial_places():
        db_path = get_spatial_db_path(create=True)
        if not db_path:
            raise HTTPException(status_code=404, detail="Spatial database not found")
        rows = fetch_spatial_rows(db_path, "SELECT * FROM places")
        return {"places": rows}

    @router.get("/spatial/file-tags")
    async def spatial_file_tags():
        db_path = get_spatial_db_path(create=True)
        if not db_path:
            raise HTTPException(status_code=404, detail="Spatial database not found")
        rows = fetch_spatial_rows(
            db_path,
            """
            SELECT f.file_path, ft.place_id, ft.source, ft.created_at, p.anchor_id, p.space, p.loc_id
            FROM file_place_tags ft
            JOIN places p ON ft.place_id = p.place_id
            JOIN files f ON ft.file_path = f.file_path
            """,
        )
        return {"file_tags": rows}

    @router.post("/render")
    async def trigger_render(
        payload: Optional[RenderRequest] = Body(None),
        theme: Optional[str] = Query(None),
    ):
        resolved_theme = theme or (payload.theme if payload else None)
        if not resolved_theme:
            raise HTTPException(status_code=400, detail="Theme is required")
        mission_id = payload.mission_id if payload else None
        result = _invoke_renderer(resolved_theme, mission_id)
        job_id = result.get("job_id") or f"job-{uuid.uuid4()}"
        real_mission_id = result.get("mission_id") or mission_id or f"renderer-{resolved_theme}"
        return {
            "status": result.get("status", "completed"),
            "job_id": job_id,
            "mission_id": real_mission_id,
            "theme": resolved_theme,
            "rendered": result.get("renderedFiles", result.get("files", [])),
            "nav": result.get("nav", []),
            "started_at": result.get("started_at"),
            "completed_at": result.get("completed_at"),
            "mission_output_path": f"06_RUNS/{real_mission_id}/{job_id}.json",
            "submitted_at": datetime.utcnow().isoformat() + "Z",
        }

    return router
