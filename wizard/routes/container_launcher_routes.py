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

from wizard.services.path_utils import get_repo_root
from wizard.services.logging_api import get_logger

logger = get_logger("container-launcher")

router = APIRouter(prefix="/api/containers", tags=["containers"])


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


def get_launcher() -> ContainerLauncher:
    """Get or create container launcher."""
    global _launcher
    if _launcher is None:
        _launcher = ContainerLauncher()
    return _launcher


# Routes
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
