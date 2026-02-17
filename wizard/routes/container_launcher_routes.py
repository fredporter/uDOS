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

    CONTAINER_CONFIGS = {
        "home-assistant": {
            "name": "Home Assistant",
            "port": 8123,
            "service_path": "wizard/services/home_assistant",
            "launch_command": ["python", "-m", "wizard.services.home_assistant"],
            "health_check_url": "http://localhost:8123/api/",
            "browser_route": "/ui/home-assistant",
        },
        "songscribe": {
            "name": "Songscribe",
            "port": 3000,
            "service_path": "wizard/services/songscribe",
            "launch_command": ["npm", "run", "dev"],
            "health_check_url": "http://localhost:3000",
            "browser_route": "/ui/songscribe",
        },
        "hethack": {
            "name": "TOYBOX Dungeon (hethack)",
            "port": 7421,
            "service_path": "wizard/services/toybox",
            "launch_command": ["python3", "-m", "wizard.services.toybox.hethack_adapter"],
            "health_check_url": "http://localhost:7421/health",
            "browser_route": "/ui/hethack",
        },
        "elite": {
            "name": "TOYBOX Galaxy (elite)",
            "port": 7422,
            "service_path": "wizard/services/toybox",
            "launch_command": ["python3", "-m", "wizard.services.toybox.elite_adapter"],
            "health_check_url": "http://localhost:7422/health",
            "browser_route": "/ui/elite",
        },
        "rpgbbs": {
            "name": "TOYBOX Social Dungeon (rpgbbs)",
            "port": 7423,
            "service_path": "wizard/services/toybox",
            "launch_command": ["python3", "-m", "wizard.services.toybox.rpgbbs_adapter"],
            "health_check_url": "http://localhost:7423/health",
            "browser_route": "/ui/rpgbbs",
        },
        "crawler3d": {
            "name": "TOYBOX Crawler Lens (crawler3d)",
            "port": 7424,
            "service_path": "wizard/services/toybox",
            "launch_command": ["python3", "-m", "wizard.services.toybox.crawler3d_adapter"],
            "health_check_url": "http://localhost:7424/health",
            "browser_route": "/ui/crawler3d",
        },
    }

    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or get_repo_root()
        self.processes: Dict[str, subprocess.Popen] = {}
        self.library_root = self.repo_root / "library"

    def get_container_config(self, container_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a container."""
        return self.CONTAINER_CONFIGS.get(container_id)

    def is_running(self, container_id: str) -> bool:
        """Check if container is running."""
        proc = self.processes.get(container_id)
        return proc is not None and proc.poll() is None

    async def launch_container(self, container_id: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """Launch a containerized plugin."""
        config = self.get_container_config(container_id)
        if not config:
            raise HTTPException(status_code=404, detail=f"Container not found: {container_id}")

        if self.is_running(container_id):
            return {
                "success": True,
                "status": "already_running",
                "port": config["port"],
                "browser_route": config["browser_route"],
            }

        # Read container.json for launch config
        container_json_path = self.library_root / container_id / "container.json"
        if not container_json_path.exists():
            raise HTTPException(status_code=404, detail=f"Container metadata not found: {container_id}")

        try:
            container_metadata = json.loads(container_json_path.read_text())
            launch_config = container_metadata.get("launch_config", {})

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
                "message": f"Launching {config['name']}..."
            }
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
        if not self.is_running(container_id):
            return {"success": True, "status": "not_running"}

        proc = self.processes.get(container_id)
        try:
            proc.terminate()
            proc.wait(timeout=5)
            del self.processes[container_id]
            logger.info(f"[CONTAINER-LAUNCHER] Stopped {container_id}")
            return {"success": True, "status": "stopped"}
        except Exception as e:
            logger.error(f"[CONTAINER-LAUNCHER] Error stopping {container_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to stop container: {str(e)}")

    async def get_status(self, container_id: str) -> Dict[str, Any]:
        """Get status of a container."""
        config = self.get_container_config(container_id)
        if not config:
            raise HTTPException(status_code=404, detail=f"Container not found: {container_id}")

        running = self.is_running(container_id)
        return {
            "success": True,
            "container_id": container_id,
            "name": config["name"],
            "running": running,
            "port": config["port"],
            "browser_route": config["browser_route"],
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


@router.get("/list/available")
async def list_available_containers(request: Request):
    """List all available containers."""
    launcher = get_launcher()
    containers = []
    for container_id, config in launcher.CONTAINER_CONFIGS.items():
        containers.append({
            "id": container_id,
            "name": config["name"],
            "port": config["port"],
            "browser_route": config["browser_route"],
            "running": launcher.is_running(container_id),
        })
    return {"success": True, "containers": containers}
