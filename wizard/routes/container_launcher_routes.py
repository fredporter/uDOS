"""
Container Launcher Routes
=========================

Routes for launching and managing containerized plugins (home-assistant, songscribe, etc)
from the Wizard GUI with browser output pages.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import subprocess
import asyncio
import shutil
from datetime import datetime
from pydantic import BaseModel, Field

from wizard.services.path_utils import get_repo_root
from wizard.services.logging_api import get_logger

logger = get_logger("container-launcher")

router = APIRouter(prefix="/api/containers", tags=["containers"])


class ComposeUpRequest(BaseModel):
    profiles: List[str] = Field(default_factory=list)
    build: bool = False
    detach: bool = True


class ComposeDownRequest(BaseModel):
    profiles: List[str] = Field(default_factory=list)
    remove_orphans: bool = True


class ComposeOrchestrator:
    VALID_PROFILES = {"scheduler", "homeassistant", "groovebox", "all"}

    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or get_repo_root()
        self.compose_file = self.repo_root / "docker-compose.yml"

    def _normalize_profiles(self, profiles: Optional[List[str]]) -> List[str]:
        normalized = [p.strip().lower() for p in (profiles or []) if p and p.strip()]
        invalid = sorted([p for p in normalized if p not in self.VALID_PROFILES])
        if invalid:
            raise HTTPException(status_code=400, detail=f"Invalid compose profiles: {', '.join(invalid)}")
        if "all" in normalized:
            return ["all"]
        deduped: List[str] = []
        seen = set()
        for profile in normalized:
            if profile not in seen:
                seen.add(profile)
                deduped.append(profile)
        return deduped

    def _docker_available(self) -> bool:
        if shutil.which("docker") is None:
            return False
        probe = subprocess.run(
            ["docker", "compose", "version"],
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return probe.returncode == 0

    def _compose_base_cmd(self, profiles: List[str]) -> List[str]:
        cmd = ["docker", "compose", "-f", str(self.compose_file)]
        for profile in profiles:
            cmd.extend(["--profile", profile])
        return cmd

    def up(self, profiles: Optional[List[str]] = None, build: bool = False, detach: bool = True) -> Dict[str, Any]:
        normalized = self._normalize_profiles(profiles)
        if not self._docker_available():
            return {"success": False, "detail": "docker compose unavailable", "profiles": normalized}

        cmd = self._compose_base_cmd(normalized) + ["up"]
        if detach:
            cmd.append("-d")
        if build:
            cmd.append("--build")

        proc = subprocess.run(
            cmd,
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
            timeout=180,
        )
        return {
            "success": proc.returncode == 0,
            "profiles": normalized,
            "command": cmd,
            "stdout": (proc.stdout or "").strip()[:2000],
            "stderr": (proc.stderr or "").strip()[:2000],
        }

    def down(self, profiles: Optional[List[str]] = None, remove_orphans: bool = True) -> Dict[str, Any]:
        normalized = self._normalize_profiles(profiles)
        if not self._docker_available():
            return {"success": False, "detail": "docker compose unavailable", "profiles": normalized}

        cmd = self._compose_base_cmd(normalized) + ["down"]
        if remove_orphans:
            cmd.append("--remove-orphans")

        proc = subprocess.run(
            cmd,
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
            timeout=180,
        )
        return {
            "success": proc.returncode == 0,
            "profiles": normalized,
            "command": cmd,
            "stdout": (proc.stdout or "").strip()[:2000],
            "stderr": (proc.stderr or "").strip()[:2000],
        }

    def status(self) -> Dict[str, Any]:
        available_profiles = sorted(list(self.VALID_PROFILES))
        if not self._docker_available():
            return {
                "success": False,
                "docker_available": False,
                "profiles": available_profiles,
                "running_services": [],
            }

        cmd = ["docker", "compose", "-f", str(self.compose_file), "ps", "--services", "--filter", "status=running"]
        proc = subprocess.run(
            cmd,
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        running = [line.strip() for line in (proc.stdout or "").splitlines() if line.strip()]
        return {
            "success": proc.returncode == 0,
            "docker_available": True,
            "profiles": available_profiles,
            "running_services": running,
        }


class ContainerLauncher:
    """Manages launching and monitoring containerized plugins."""

    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or get_repo_root()
        self.processes: Dict[str, subprocess.Popen] = {}
        self.library_root = self.repo_root / "library"

    def _discover_containers(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all launchable containers by scanning library/*/container.json.
        A container is launchable if it has a service.port defined.
        Returns a dict keyed by container id.
        """
        found: Dict[str, Dict[str, Any]] = {}
        if not self.library_root.exists():
            return found
        for entry in sorted(self.library_root.iterdir()):
            if not entry.is_dir():
                continue
            cj = entry / "container.json"
            if not cj.exists():
                continue
            try:
                manifest = json.loads(cj.read_text())
            except Exception:
                continue
            container_section = manifest.get("container", {})
            service_section = manifest.get("service", {})
            port = service_section.get("port")
            if not port:
                continue  # not a runnable service
            cid = container_section.get("id") or entry.name
            found[cid] = {
                "name": container_section.get("name", cid),
                "port": port,
                "health_check_url": service_section.get("health_check_url"),
                "browser_route": service_section.get("browser_route", f"/ui/{cid}"),
            }
        return found

    @property
    def CONTAINER_CONFIGS(self) -> Dict[str, Dict[str, Any]]:
        """Live view of launchable containers discovered from library manifests."""
        return self._discover_containers()

    def get_container_config(self, container_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a container."""
        return self._discover_containers().get(container_id)

    def is_running(self, container_id: str) -> bool:
        """Check if container is running."""
        proc = self.processes.get(container_id)
        return proc is not None and proc.poll() is None

    def _read_container_metadata(self, container_id: str) -> Optional[Dict[str, Any]]:
        """Read container.json for a library entry. Returns None if not found."""
        container_json_path = self.library_root / container_id / "container.json"
        if not container_json_path.exists():
            return None
        try:
            return json.loads(container_json_path.read_text())
        except Exception:
            return None

    def _container_state(self, container_id: str) -> str:
        """
        Return detailed state string for a container:
          'not_found'     — not in CONTAINER_CONFIGS
          'no_metadata'   — container.json missing
          'not_cloned'    — git-type but repo not yet cloned
          'not_running'   — known but not running
          'running'       — process is running
        """
        if container_id not in self.CONTAINER_CONFIGS:
            return "not_found"
        meta = self._read_container_metadata(container_id)
        if meta is None:
            return "no_metadata"
        container_section = meta.get("container", {})
        ctype = container_section.get("type", "local")
        if ctype == "git":
            cloned_at = container_section.get("cloned_at")
            # Check both: library/<id>/.git (in-place) and library/containers/<id>/.git (PluginFactory clone dest)
            git_dir_inplace = self.library_root / container_id / ".git"
            git_dir_containers = self.library_root / "containers" / container_id / ".git"
            if not cloned_at and not git_dir_inplace.exists() and not git_dir_containers.exists():
                return "not_cloned"
        if self.is_running(container_id):
            return "running"
        return "not_running"

    async def launch_container(self, container_id: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """Launch a containerized plugin."""
        config = self.get_container_config(container_id)
        if not config:
            raise HTTPException(status_code=404, detail=f"Container not found: {container_id}")

        state = self._container_state(container_id)

        if state == "running":
            return {
                "success": True,
                "status": "already_running",
                "container_id": container_id,
                "port": config["port"],
                "browser_route": config["browser_route"],
                "steps": [{"step": "check", "result": "already running", "ok": True}],
            }

        if state == "no_metadata":
            raise HTTPException(status_code=404, detail=f"Container metadata not found: {container_id}")

        if state == "not_cloned":
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Container {container_id} is a git-type library entry that has not been cloned yet. "
                    f"Clone it via POST /api/library/repos/clone before launching."
                ),
            )

        try:
            container_metadata = self._read_container_metadata(container_id)
            launch_config = (container_metadata or {}).get("launch_config", {})

            # Schedule container launch in background
            background_tasks.add_task(
                self._launch_service,
                container_id,
                config,
                launch_config
            )

            return {
                "success": True,
                "status": "launching",
                "container_id": container_id,
                "name": config["name"],
                "port": config["port"],
                "browser_route": config["browser_route"],
                "steps": [
                    {"step": "validate", "result": "metadata ok", "ok": True},
                    {"step": "launch", "result": "scheduled in background", "ok": True},
                ],
                "message": f"Launching {config['name']}...",
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[CONTAINER-LAUNCHER] Failed to launch {container_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to launch container: {str(e)}")

    async def _launch_service(self, container_id: str, config: Dict[str, Any], launch_config: Dict[str, Any]):
        """Launch service in background."""
        try:
            container_path = self.library_root / container_id
            launch_cwd = container_path
            custom_cwd = launch_config.get("cwd")
            if custom_cwd:
                cwd_path = Path(custom_cwd)
                if not cwd_path.is_absolute():
                    cwd_path = self.repo_root / cwd_path
                launch_cwd = cwd_path

            # Build command
            cmd = launch_config.get("command")
            if not cmd:
                cmd = config.get("launch_command", ["python", "-m", f"wizard.services.{container_id}"])

            logger.info(f"[CONTAINER-LAUNCHER] Starting {container_id} with command: {cmd}")

            # Launch process
            proc = subprocess.Popen(
                cmd,
                cwd=str(launch_cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.processes[container_id] = proc

            # Wait for health check
            await self._wait_for_health(container_id, config, max_retries=30)

            logger.info(f"[CONTAINER-LAUNCHER] {container_id} is ready")

        except Exception as e:
            logger.error(f"[CONTAINER-LAUNCHER] Error launching {container_id}: {str(e)}")
            if container_id in self.processes:
                del self.processes[container_id]

    async def _wait_for_health(self, container_id: str, config: Dict[str, Any], max_retries: int = 30):
        """Wait for container to be healthy."""
        import httpx

        health_url = config.get("health_check_url")
        if not health_url:
            await asyncio.sleep(2)  # Give it a moment to start
            return

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(health_url, timeout=2.0)
                    if response.status_code < 500:
                        return  # Healthy
            except Exception:
                pass

            await asyncio.sleep(1)

        logger.warn(f"[CONTAINER-LAUNCHER] {container_id} health check timed out")

    async def stop_container(self, container_id: str) -> Dict[str, Any]:
        """Stop a running container."""
        steps: List[Dict[str, Any]] = []

        if not self.is_running(container_id):
            steps.append({"step": "check", "result": "not running", "ok": True})
            return {"success": True, "status": "not_running", "steps": steps}

        proc = self.processes.get(container_id)
        steps.append({"step": "check", "result": "running — stopping", "ok": True})
        try:
            proc.terminate()
            steps.append({"step": "terminate", "result": "SIGTERM sent", "ok": True})
            proc.wait(timeout=5)
            del self.processes[container_id]
            steps.append({"step": "wait", "result": "process exited", "ok": True})
            logger.info(f"[CONTAINER-LAUNCHER] Stopped {container_id}")
            return {"success": True, "status": "stopped", "steps": steps}
        except Exception as e:
            steps.append({"step": "wait", "result": str(e), "ok": False})
            logger.error(f"[CONTAINER-LAUNCHER] Error stopping {container_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to stop container: {str(e)}")

    def _get_clone_params(self, container_id: str):
        """Validate and return (source, ref, clone_dest) or raise HTTPException."""
        if container_id not in self.CONTAINER_CONFIGS:
            raise HTTPException(status_code=404, detail=f"Container not found: {container_id}")
        meta = self._read_container_metadata(container_id)
        if meta is None:
            raise HTTPException(status_code=404, detail=f"container.json missing for {container_id}")
        container_section = meta.get("container", {})
        if container_section.get("type", "local") != "git":
            raise HTTPException(status_code=400, detail=f"Container {container_id} is not type 'git'")
        source = container_section.get("source", "")
        if not source:
            raise HTTPException(status_code=400, detail=f"No source URL in container.json for {container_id}")
        ref = container_section.get("ref") or "main"
        clone_dest = self.library_root / "containers" / container_id
        return source, ref, clone_dest

    def _stamp_cloned_at(self, container_id: str):
        """Write cloned_at timestamp into library/<id>/container.json."""
        container_json_path = self.library_root / container_id / "container.json"
        if container_json_path.exists():
            try:
                manifest = json.loads(container_json_path.read_text())
                manifest.setdefault("container", {})["cloned_at"] = datetime.utcnow().isoformat() + "Z"
                container_json_path.write_text(json.dumps(manifest, indent=2))
                return True, "cloned_at written to container.json"
            except Exception as e:
                return False, str(e)
        return False, "container.json not found"

    async def stream_clone(self, container_id: str):
        """
        SSE generator: streams git clone progress as JSON events.
        Each event: data: {"progress": 0-100, "status": str, "message": str}
        Final event on success: {"progress": 100, "status": "complete", ...}
        Final event on failure: {"progress": N, "status": "failed", "error": str}
        """
        from fastapi.responses import StreamingResponse

        try:
            source, ref, clone_dest = self._get_clone_params(container_id)
        except HTTPException as e:
            async def _err():
                yield f"data: {json.dumps({'progress': 0, 'status': 'failed', 'error': e.detail})}\n\n"
            return StreamingResponse(_err(), media_type="text/event-stream")

        async def generate():
            yield f"data: {json.dumps({'progress': 0, 'status': 'starting', 'message': f'Preparing to clone {container_id}...'})}\n\n"

            # Already cloned?
            if clone_dest.exists() and (clone_dest / ".git").exists():
                ok, msg = self._stamp_cloned_at(container_id)
                yield f"data: {json.dumps({'progress': 100, 'status': 'complete', 'message': 'Already cloned. State updated.'})}\n\n"
                return

            yield f"data: {json.dumps({'progress': 5, 'status': 'cloning', 'message': f'git clone --depth 1 {source} @ {ref}'})}\n\n"
            clone_dest.parent.mkdir(parents=True, exist_ok=True)

            try:
                proc = await asyncio.create_subprocess_exec(
                    "git", "clone", "--depth", "1", "--branch", ref,
                    "--progress", source, str(clone_dest),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            except FileNotFoundError:
                yield f"data: {json.dumps({'progress': 5, 'status': 'failed', 'error': 'git not found in PATH'})}\n\n"
                return

            progress = 10
            # git clone writes progress to stderr
            async for line in proc.stderr:
                text = line.decode(errors="replace").strip()
                if not text:
                    continue
                progress = min(progress + 3, 90)
                yield f"data: {json.dumps({'progress': progress, 'status': 'cloning', 'message': text[:120]})}\n\n"

            await proc.wait()

            if proc.returncode != 0:
                stdout = await proc.stdout.read()
                err = stdout.decode(errors="replace").strip()[:200] or f"git exited {proc.returncode}"
                logger.error(f"[CONTAINER-LAUNCHER] Clone failed for {container_id}: {err}")
                yield f"data: {json.dumps({'progress': progress, 'status': 'failed', 'error': err})}\n\n"
                return

            yield f"data: {json.dumps({'progress': 95, 'status': 'stamping', 'message': 'Updating container manifest...'})}\n\n"
            ok, stamp_msg = self._stamp_cloned_at(container_id)
            logger.info(f"[CONTAINER-LAUNCHER] Cloned {container_id} from {source}")
            yield f"data: {json.dumps({'progress': 100, 'status': 'complete', 'message': f'✅ {container_id} cloned successfully', 'clone_path': str(clone_dest)})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    async def clone_container(self, container_id: str) -> Dict[str, Any]:
        """Blocking clone (kept for non-SSE callers). Returns steps summary."""
        source, ref, clone_dest = self._get_clone_params(container_id)
        steps: List[Dict[str, Any]] = []

        if clone_dest.exists() and (clone_dest / ".git").exists():
            steps.append({"step": "check", "result": "already cloned", "ok": True})
        else:
            steps.append({"step": "check", "result": f"cloning {source} @ {ref}", "ok": True})
            try:
                clone_dest.parent.mkdir(parents=True, exist_ok=True)
                result = subprocess.run(
                    ["git", "clone", "--depth", "1", "--branch", ref, source, str(clone_dest)],
                    capture_output=True, text=True, timeout=180,
                )
                if result.returncode != 0:
                    steps.append({"step": "clone", "result": result.stderr.strip()[:300], "ok": False})
                    raise HTTPException(status_code=500, detail=f"git clone failed: {result.stderr.strip()[:200]}")
                steps.append({"step": "clone", "result": "cloned ok", "ok": True})
            except FileNotFoundError:
                raise HTTPException(status_code=500, detail="git not found in PATH")
            except subprocess.TimeoutExpired:
                raise HTTPException(status_code=504, detail=f"git clone timed out for {source}")

        ok, stamp_msg = self._stamp_cloned_at(container_id)
        steps.append({"step": "stamp", "result": stamp_msg, "ok": ok})
        logger.info(f"[CONTAINER-LAUNCHER] Cloned {container_id} from {source}")
        return {"success": True, "container_id": container_id, "source": source, "ref": ref,
                "clone_path": str(clone_dest), "steps": steps}

    async def get_status(self, container_id: str) -> Dict[str, Any]:
        """Get detailed status of a container."""
        config = self.get_container_config(container_id)
        if not config:
            raise HTTPException(status_code=404, detail=f"Container not found: {container_id}")

        state = self._container_state(container_id)
        meta = self._read_container_metadata(container_id)
        container_section = (meta or {}).get("container", {})

        return {
            "success": True,
            "container_id": container_id,
            "name": config["name"],
            "state": state,
            "running": state == "running",
            "port": config["port"],
            "browser_route": config["browser_route"],
            "container_type": container_section.get("type", "local"),
            "git_cloned": state not in ("not_cloned", "no_metadata"),
            "detail": {
                "not_found": "Container not registered",
                "no_metadata": "container.json missing from library entry",
                "not_cloned": "Git repo not yet cloned — use /api/library/repos/clone",
                "not_running": f"Container is ready but not running — use /api/containers/{container_id}/launch",
                "running": f"Running on port {config['port']}",
            }.get(state, state),
        }


# Create singleton launcher
_launcher: Optional[ContainerLauncher] = None
_orchestrator: Optional[ComposeOrchestrator] = None


def get_launcher() -> ContainerLauncher:
    """Get or create container launcher."""
    global _launcher
    if _launcher is None:
        _launcher = ContainerLauncher()
    return _launcher


def get_orchestrator() -> ComposeOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ComposeOrchestrator()
    return _orchestrator


# Routes
@router.post("/compose/up", response_model=Dict[str, Any])
async def compose_up(payload: ComposeUpRequest, request: Request):
    orchestrator = get_orchestrator()
    result = orchestrator.up(
        profiles=payload.profiles,
        build=payload.build,
        detach=payload.detach,
    )
    if not result.get("success"):
        detail = result.get("detail") or result.get("stderr") or "compose up failed"
        raise HTTPException(status_code=500, detail=detail)
    return result


@router.post("/compose/down", response_model=Dict[str, Any])
async def compose_down(payload: ComposeDownRequest, request: Request):
    orchestrator = get_orchestrator()
    result = orchestrator.down(
        profiles=payload.profiles,
        remove_orphans=payload.remove_orphans,
    )
    if not result.get("success"):
        detail = result.get("detail") or result.get("stderr") or "compose down failed"
        raise HTTPException(status_code=500, detail=detail)
    return result


@router.get("/compose/status", response_model=Dict[str, Any])
async def compose_status(request: Request):
    orchestrator = get_orchestrator()
    return orchestrator.status()


@router.post("/{container_id}/launch")
async def launch_container(container_id: str, request: Request, background_tasks: BackgroundTasks):
    """Launch a containerized plugin."""
    launcher = get_launcher()
    return await launcher.launch_container(container_id, background_tasks)


@router.post("/{container_id}/stop")
async def stop_container(container_id: str, request: Request):
    """Stop a running container."""
    launcher = get_launcher()
    return await launcher.stop_container(container_id)


@router.get("/{container_id}/status")
async def get_container_status(container_id: str, request: Request):
    """Get container status."""
    launcher = get_launcher()
    return await launcher.get_status(container_id)


@router.post("/{container_id}/clone")
async def clone_container(container_id: str, request: Request):
    """Clone a git-type container repo from its container.json source URL (blocking)."""
    launcher = get_launcher()
    return await launcher.clone_container(container_id)


@router.get("/{container_id}/clone/stream")
async def stream_clone_container(container_id: str, request: Request):
    """Clone a git-type container with SSE progress streaming.
    Client reads text/event-stream; each event is a JSON object:
      { progress: 0-100, status: "starting"|"cloning"|"stamping"|"complete"|"failed", message: str }
    """
    launcher = get_launcher()
    return await launcher.stream_clone(container_id)


@router.get("/list/available")
async def list_available_containers(request: Request):
    """List all available containers with detailed state."""
    launcher = get_launcher()
    containers = []
    for container_id, config in launcher.CONTAINER_CONFIGS.items():
        state = launcher._container_state(container_id)
        meta = launcher._read_container_metadata(container_id)
        container_section = (meta or {}).get("container", {})
        containers.append({
            "id": container_id,
            "name": config["name"],
            "port": config["port"],
            "browser_route": config["browser_route"],
            "state": state,
            "running": state == "running",
            "container_type": container_section.get("type", "local"),
            "git_cloned": state not in ("not_cloned", "no_metadata"),
        })
    return {"success": True, "containers": containers}
