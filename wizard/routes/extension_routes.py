"""
Extension detection routes for Wizard Server.

Reports which official uDOS extensions are present on the local system.
Extensions are private submodules and only appear if installed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Request

from wizard.services.path_utils import get_repo_root

REPO_ROOT = get_repo_root()

# Official uDOS extensions (submodules)
# visibility: "private" = Extensions page only (if installed), "public" = both Plugins + Extensions
OFFICIAL_EXTENSIONS = [
    {
        "id": "empire",
        "name": "Empire",
        "description": "Commercial business extension: contacts, email, data enrichment",
        "icon": "🏛",
        "path": "empire",
        "main_file": "src/spine.py",
        "api_prefix": "/api/empire",
        "web_port": 8991,
        "category": "business",
        "visibility": "private",
    },
    {
        "id": "dev",
        "name": "Dev Mode",
        "description": "Developer tooling, debugging, and internal utilities",
        "icon": "🧌",
        "path": "dev",
        "main_file": "__init__.py",
        "api_prefix": "/api/dev",
        "web_port": None,
        "category": "developer",
        "visibility": "public",
    },
    {
        "id": "groovebox",
        "name": "Groovebox",
        "description": "Audio sample library and playback tools",
        "icon": "🎛",
        "path": "wizard/groovebox",
        "main_file": "sample-library.json",
        "api_prefix": "/api/groovebox",
        "web_port": None,
        "category": "audio",
        "visibility": "private",
    },
    {
        "id": "sonic",
        "name": "Sonic Screwdriver",
        "description": "Multi-tool utilities for data transformation and scripting",
        "icon": "🔧",
        "path": "sonic",
        "main_file": "__init__.py",
        "api_prefix": "/api/sonic",
        "web_port": None,
        "category": "utilities",
        "visibility": "public",
    },
]


def _check_extension_present(ext: Dict[str, Any]) -> bool:
    """Check if extension submodule is present on the local system."""
    ext_path = REPO_ROOT / ext["path"]
    if not ext_path.exists() or not ext_path.is_dir():
        return False
    # Check for main file to ensure it's not an empty submodule
    main_file = ext_path / ext["main_file"]
    return main_file.exists()


def _get_extension_status(ext: Dict[str, Any]) -> Dict[str, Any]:
    """Get full status for an extension."""
    present = _check_extension_present(ext)
    ext_path = REPO_ROOT / ext["path"]

    result = {
        "id": ext["id"],
        "name": ext["name"],
        "description": ext["description"],
        "icon": ext["icon"],
        "category": ext["category"],
        "present": present,
        "api_prefix": ext["api_prefix"],
        "web_port": ext["web_port"],
        "visibility": ext.get("visibility", "public"),
    }

    if present:
        # Try to get version info
        version_file = ext_path / "version.json"
        if version_file.exists():
            try:
                import json
                version_data = json.loads(version_file.read_text())
                result["version"] = version_data.get("version", "unknown")
            except Exception:
                result["version"] = "unknown"
        else:
            result["version"] = "dev"

    return result


router = APIRouter(prefix="/api/extensions", tags=["extensions"])


@router.get("/list")
async def list_extensions(request: Request, visibility: Optional[str] = None) -> Dict[str, Any]:
    """List all official extensions and their availability.

    Args:
        visibility: Filter by visibility ("public", "private", or None for all)
    """
    extensions = []
    for ext in OFFICIAL_EXTENSIONS:
        ext_status = _get_extension_status(ext)
        # Filter by visibility if specified
        if visibility and ext_status["visibility"] != visibility:
            continue
        # For private extensions, only show if present on local system
        if ext_status["visibility"] == "private" and not ext_status["present"]:
            continue
        extensions.append(ext_status)

    present_count = sum(1 for e in extensions if e["present"])

    return {
        "extensions": extensions,
        "summary": {
            "total": len(extensions),
            "present": present_count,
            "missing": len(extensions) - present_count,
        },
    }


@router.get("/status/{extension_id}")
async def extension_status(extension_id: str, request: Request) -> Dict[str, Any]:
    """Get detailed status for a specific extension."""
    for ext in OFFICIAL_EXTENSIONS:
        if ext["id"] == extension_id:
            return _get_extension_status(ext)

    return {"error": f"Unknown extension: {extension_id}", "present": False}


@router.get("/empire/token-status")
async def empire_token_status(request: Request) -> Dict[str, Any]:
    """Check if Empire API token is configured."""
    ext_path = REPO_ROOT / "empire"
    secrets_file = ext_path / "config" / "empire_secrets.json"
    key_file = ext_path / "config" / ".empire_key"

    has_secrets = secrets_file.exists()
    has_key = key_file.exists()

    token_configured = False
    if has_secrets:
        try:
            import json
            secrets = json.loads(secrets_file.read_text())
            token_configured = bool(secrets.get("empire_api_token"))
        except Exception:
            pass

    return {
        "present": (ext_path / "src" / "spine.py").exists(),
        "key_file_exists": has_key,
        "secrets_file_exists": has_secrets,
        "token_configured": token_configured,
    }
