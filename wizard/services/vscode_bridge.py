"""
VSCode Extension API Bridge
============================

Exposes /api/* endpoints that the VSCode extension expects,
bridging to uDOS core services and Wizard capabilities.
"""

from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

# Core imports
try:
    from wizard.services.logging_api import get_logger
    from core.version import get_all_versions

    UDOS_AVAILABLE = True
except ImportError:
    UDOS_AVAILABLE = False
    get_logger = None
    get_all_versions = None

logger = get_logger("wizard-vscode-bridge") if get_logger else None


# Request models
class ExecuteScriptRequest(BaseModel):
    file: str
    content: str


class ExecuteCodeRequest(BaseModel):
    code: str


class CommandRequest(BaseModel):
    command: str


class SyntaxCheckRequest(BaseModel):
    code: str


def create_vscode_bridge_router() -> APIRouter:
    """Create FastAPI router for VSCode extension endpoints."""
    router = APIRouter(prefix="/api", tags=["VSCode Bridge"])

    @router.get("/health")
    async def health():
        """Health check endpoint for VSCode extension."""
        return {"status": "ok", "server": "wizard", "udos_available": UDOS_AVAILABLE}

    @router.get("/status")
    async def status():
        """System status endpoint."""
        if not UDOS_AVAILABLE:
            return {
                "status": "limited",
                "versions": {},
                "uptime": 0,
                "message": "uDOS core not available",
            }

        try:
            versions = get_all_versions()
            return {
                "status": "ok",
                "versions": versions,
                "uptime": 0,  # TODO: Track server uptime
            }
        except Exception as e:
            if logger:
                logger.error(f"Error getting status: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/execute/script")
    async def execute_script(request: ExecuteScriptRequest):
        """Execute a TypeScript script file (embedded in .md)."""
        if not UDOS_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="uDOS core not available - execution requires full uDOS installation",
            )

        # TODO: Implement script execution via uDOS core
        if logger:
            logger.warning(
                f"[WIZ] Script execution not yet implemented: {request.file}"
            )

        return {
            "success": False,
            "error": "Script execution not yet implemented in Wizard mode",
            "output": "Use uDOS TUI for full script execution",
        }

    @router.post("/execute/code")
    async def execute_code(request: ExecuteCodeRequest):
        """Execute TypeScript code snippet."""
        if not UDOS_AVAILABLE:
            raise HTTPException(status_code=503, detail="uDOS core not available")

        # TODO: Implement code execution via uDOS core
        if logger:
            logger.warning(
                f"[WIZ] Code execution not yet implemented: {len(request.code)} chars"
            )

        return {
            "success": False,
            "error": "Code execution not yet implemented in Wizard mode",
            "output": "Use uDOS TUI for full code execution",
        }

    @router.post("/command")
    async def execute_command(request: CommandRequest):
        """Execute a uDOS command."""
        if not UDOS_AVAILABLE:
            raise HTTPException(status_code=503, detail="uDOS core not available")

        # TODO: Implement command routing via uDOS core
        if logger:
            logger.info(f"[WIZ] Command request: {request.command}")

        return {
            "success": False,
            "error": "Command execution not yet implemented in Wizard mode",
            "result": "Use uDOS TUI for command execution",
        }

    @router.post("/script/check")
    async def check_syntax(request: SyntaxCheckRequest):
        """Check TypeScript syntax."""
        # Basic validation - can be enhanced later
        lines = request.code.split("\n")
        errors = []

        # Simple block depth check
        block_depth = 0
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped.startswith("#"):
                continue

            # Check for block start keywords
            if any(
                kw in line_stripped.upper() for kw in ["FUNCTION", "IF", "FOR", "WHILE"]
            ):
                block_depth += 1

            # Check for block end keywords
            if any(kw in line_stripped.upper() for kw in ["END", "NEXT", "WEND"]):
                block_depth -= 1

            if block_depth < 0:
                errors.append({"line": i + 1, "message": "Unexpected block end"})
                block_depth = 0

        if block_depth > 0:
            errors.append(
                {"line": len(lines), "message": f"{block_depth} unclosed block(s)"}
            )

        return {"valid": len(errors) == 0, "errors": errors}

    @router.get("/knowledge/tree")
    async def get_knowledge_tree():
        """Get knowledge bank file tree."""
        try:
            # Get knowledge directory
            from pathlib import Path

            knowledge_dir = Path(__file__).parent.parent.parent / "knowledge"

            if not knowledge_dir.exists():
                return {"tree": []}

            def build_tree(path: Path) -> Dict[str, Any]:
                """Build tree recursively."""
                if path.is_file():
                    return {
                        "name": path.name,
                        "path": str(path.relative_to(knowledge_dir)),
                        "type": "file",
                    }
                else:
                    children = []
                    for child in sorted(path.iterdir()):
                        if child.name.startswith("."):
                            continue
                        children.append(build_tree(child))

                    return {
                        "name": path.name,
                        "path": str(path.relative_to(knowledge_dir)),
                        "type": "directory",
                        "children": children,
                    }

            tree = []
            for item in sorted(knowledge_dir.iterdir()):
                if item.name.startswith(".") or item.name in [
                    "__pycache__",
                    "version.json",
                ]:
                    continue
                tree.append(build_tree(item))

            return {"tree": tree}

        except Exception as e:
            if logger:
                logger.error(f"Error building knowledge tree: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/files/read")
    async def read_file(path: str):
        """Read file content."""
        try:
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent
            file_path = project_root / path

            if not file_path.exists():
                raise HTTPException(status_code=404, detail="File not found")

            if not file_path.is_file():
                raise HTTPException(status_code=400, detail="Not a file")

            # Security check - ensure file is within project
            try:
                file_path.resolve().relative_to(project_root.resolve())
            except ValueError:
                raise HTTPException(status_code=403, detail="Access denied")

            content = file_path.read_text(encoding="utf-8")
            return {"content": content}

        except HTTPException:
            raise
        except Exception as e:
            if logger:
                logger.error(f"Error reading file {path}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return router
