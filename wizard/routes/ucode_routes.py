"""
uCODE Bridge Routes
===================

Expose a minimal, allowlisted uCODE command dispatch endpoint for Vibe/MCP.
"""

from __future__ import annotations

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Generator

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import subprocess
from pydantic import BaseModel

from wizard.services.logging_api import get_logger, new_corr_id
from core.services.logging_api import set_corr_id, reset_corr_id

class DispatchRequest(BaseModel):
    command: str
    ok_model: Optional[str] = None
    ok_context_window: Optional[int] = None


def _default_allowlist() -> set[str]:
    base = {
        "STATUS",
        "HELP",
        "MAP",
        "PANEL",
        "FIND",
        "TELL",
        "GOTO",
        "BAG",
        "GRAB",
        "SPAWN",
        "STORY",
        "RUN",
        "BINDER",
        "DATASET",
        "USER",
        "UID",
        "DEV",
        "WIZARD",
        "CONFIG",
        "SAVE",
        "LOAD",
        "FILE",
        "NEW",
        "EDIT",
        "NPC",
        "TALK",
        "REPLY",
        "LOGS",
        "REPAIR",
        "SHAKEDOWN",
        "REBOOT",
        "PATTERN",
        "SONIC",
        "INTEGRATION",
        "PROVIDER",
        "SETUP",
    }
    try:
        from core.input.command_prompt import create_default_registry

        registry = create_default_registry()
        base.update({cmd.name.upper() for cmd in registry.list_all()})
    except Exception:
        pass
    return base


def _load_allowlist() -> set[str]:
    raw = os.getenv("UCODE_API_ALLOWLIST", "").strip()
    if not raw:
        return _default_allowlist()
    return {item.strip().upper() for item in raw.split(",") if item.strip()}


def _shell_allowed() -> bool:
    return os.getenv("UCODE_API_ALLOW_SHELL", "").strip().lower() in {"1", "true", "yes"}


def _shell_safe(command: str) -> bool:
    destructive_keywords = {"rm", "mv", ">", "|", "sudo", "rmdir", "dd", "format"}
    cmd_lower = command.lower()
    return not any(kw in cmd_lower for kw in destructive_keywords)


def create_ucode_routes(auth_guard=None):
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/ucode", tags=["ucode"], dependencies=dependencies)
    logger = get_logger("wizard", category="ucode", name="ucode")

    allowlist = _load_allowlist()
    ok_history: List[Dict[str, Any]] = []
    ok_counter = 0
    ok_limit = 50

    def _load_ai_modes_config() -> Dict[str, Any]:
        try:
            from core.services.logging_api import get_repo_root

            path = get_repo_root() / "core" / "config" / "ok_modes.json"
            if not path.exists():
                return {"modes": {}}
            return json.loads(path.read_text())
        except Exception:
            return {"modes": {}}

    def _write_ok_modes_config(config: Dict[str, Any]) -> None:
        from core.services.logging_api import get_repo_root

        path = get_repo_root() / "core" / "config" / "ok_modes.json"
        path.write_text(json.dumps(config, indent=2))

    def _get_ok_default_model() -> str:
        config = _load_ai_modes_config()
        mode = (config.get("modes") or {}).get("ofvibe", {})
        default_models = mode.get("default_models") or {}
        model = default_models.get("core") or default_models.get("dev")
        if os.getenv("UDOS_DEV_MODE") in ("1", "true", "yes"):
            model = default_models.get("dev") or model
        return model or "devstral-small-2"

    def _ok_auto_fallback_enabled() -> bool:
        config = _load_ai_modes_config()
        mode = (config.get("modes") or {}).get("ofvibe", {})
        return bool(mode.get("auto_fallback", True))

    def _get_ok_context_window() -> int:
        try:
            from wizard.services.vibe_service import VibeConfig

            return VibeConfig().context_window
        except Exception:
            return 8192

    def _fetch_ollama_models(endpoint: str) -> Dict[str, Any]:
        url = endpoint.rstrip("/") + "/api/tags"
        try:
            import requests

            resp = requests.get(url, timeout=2)
            if resp.status_code != 200:
                return {"reachable": False, "error": f"HTTP {resp.status_code}"}
            payload = resp.json()
            models = [m.get("name") for m in payload.get("models", []) if m.get("name")]
            return {"reachable": True, "models": models}
        except Exception as exc:
            return {"reachable": False, "error": str(exc)}

    def _get_ok_local_status() -> Dict[str, Any]:
        config = _load_ai_modes_config()
        mode = (config.get("modes") or {}).get("ofvibe", {})
        endpoint = mode.get("ollama_endpoint", "http://127.0.0.1:11434")
        model = _get_ok_default_model()
        tags = _fetch_ollama_models(endpoint)
        if not tags.get("reachable"):
            return {
                "ready": False,
                "issue": "ollama down",
                "model": model,
                "ollama_endpoint": endpoint,
                "detail": tags.get("error"),
                "models": [],
            }
        models = tags.get("models") or []
        if model and model not in models:
            return {
                "ready": False,
                "issue": "missing model",
                "model": model,
                "ollama_endpoint": endpoint,
                "detail": None,
                "models": models,
            }
        return {
            "ready": True,
            "issue": None,
            "model": model,
            "ollama_endpoint": endpoint,
            "detail": None,
            "models": models,
        }

    def _parse_ok_file_args(args: str) -> Dict[str, Any]:
        tokens = args.strip().split()
        use_cloud = False
        clean_tokens: List[str] = []
        for token in tokens:
            if token.lower() in ("--cloud", "--onvibe"):
                use_cloud = True
            else:
                clean_tokens.append(token)
        if not clean_tokens:
            return {"error": "Missing file path", "use_cloud": use_cloud}

        file_token = clean_tokens[0]
        line_start = None
        line_end = None

        if len(clean_tokens) >= 3 and clean_tokens[1].isdigit() and clean_tokens[2].isdigit():
            line_start = int(clean_tokens[1])
            line_end = int(clean_tokens[2])
        elif len(clean_tokens) >= 2 and any(sep in clean_tokens[1] for sep in (":", "-", "..")):
            parts = (
                clean_tokens[1]
                .replace("..", ":")
                .replace("-", ":")
                .split(":")
            )
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                line_start = int(parts[0])
                line_end = int(parts[1])

        from pathlib import Path

        path = Path(file_token)
        try:
            from core.services.logging_api import get_repo_root

            if not path.is_absolute():
                path = get_repo_root() / path
        except Exception:
            if not path.is_absolute():
                path = Path.cwd() / path
        return {
            "path": path,
            "line_start": line_start,
            "line_end": line_end,
            "use_cloud": use_cloud,
        }

    def _load_setup_story() -> Dict[str, Any]:
        from core.services.story_service import parse_story_document
        from wizard.services.path_utils import get_repo_root as wiz_repo_root
        from wizard.services.path_utils import get_memory_dir

        repo_root = wiz_repo_root()
        template_candidates = [
            repo_root / "core" / "tui" / "setup-story.md",
            repo_root / "core" / "framework" / "seed" / "bank" / "system" / "tui-setup-story.md",
            repo_root / "wizard" / "templates" / "tui-setup-story.md",
        ]
        memory_root = get_memory_dir()
        story_dir = memory_root / "story"
        story_dir.mkdir(parents=True, exist_ok=True)
        story_path = story_dir / "tui-setup-story.md"
        if not story_path.exists():
            template_path = next((p for p in template_candidates if p.exists()), None)
            if not template_path:
                raise HTTPException(status_code=404, detail="Setup story template missing")
            story_path.write_text(template_path.read_text())

        raw_content = story_path.read_text()
        story_state = parse_story_document(
            raw_content,
            required_frontmatter_keys=["title", "type", "submit_endpoint"],
        )
        return story_state

    def _run_ok_cloud(prompt: str) -> Tuple[str, str]:
        from wizard.services.mistral_api import MistralAPI

        config = _load_ai_modes_config()
        mode = (config.get("modes") or {}).get("onvibe", {})
        model = mode.get("default_model") or "mistral-small-latest"
        client = MistralAPI()
        return client.chat(prompt, model=model), model

    def _get_ok_cloud_status() -> Dict[str, Any]:
        try:
            from wizard.services.mistral_api import MistralAPI

            client = MistralAPI()
            if client.available():
                return {"ready": True, "issue": None}
            return {"ready": False, "issue": "mistral api key missing"}
        except Exception as exc:
            return {"ready": False, "issue": str(exc)}

    def _run_ok_local(prompt: str, model: Optional[str] = None) -> str:
        from wizard.services.vibe_service import VibeService, VibeConfig

        config = VibeConfig(model=model or _get_ok_default_model())
        vibe = VibeService(config=config)
        return vibe.generate(prompt, format="markdown")

    def _record_ok_output(
        prompt: str,
        response: str,
        model: str,
        source: str,
        mode: str,
        file_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        nonlocal ok_counter
        ok_counter += 1
        entry = {
            "id": ok_counter,
            "mode": mode,
            "prompt": prompt,
            "response": response,
            "model": model,
            "source": source,
            "file_path": file_path,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        ok_history.append(entry)
        if len(ok_history) > ok_limit:
            ok_history[:] = ok_history[-ok_limit:]
        return entry

    # Lazy imports to keep wizard usable without core in some deployments.
    try:
        from core.tui.dispatcher import CommandDispatcher
        from core.tui.state import GameState
        from core.tui.renderer import GridRenderer

        dispatcher = CommandDispatcher()
        game_state = GameState()
        renderer = GridRenderer()
    except Exception:  # pragma: no cover
        dispatcher = None
        game_state = None
        renderer = None

    @router.get("/allowlist")
    async def get_allowlist() -> Dict[str, Any]:
        return {
            "status": "ok",
            "allowlist": sorted(allowlist),
        }

    @router.get("/commands")
    async def get_commands() -> Dict[str, Any]:
        try:
            from core.input.command_prompt import create_default_registry

            registry = create_default_registry()
            registry_map = {
                cmd.name: {
                    "name": cmd.name,
                    "help_text": cmd.help_text,
                    "options": cmd.options,
                    "syntax": cmd.syntax,
                    "examples": cmd.examples,
                    "icon": cmd.icon,
                    "category": cmd.category,
                }
                for cmd in registry.list_all()
            }
        except Exception:
            registry_map = {}

        commands: List[Dict[str, Any]] = []
        for cmd in sorted(allowlist):
            base = registry_map.get(cmd) or {
                "name": cmd,
                "help_text": "Command available",
                "options": [],
                "syntax": cmd,
                "examples": [],
                "icon": "⚙️",
                "category": "General",
            }
            commands.append({**base, "allowed": True})

        ok_meta = registry_map.get("OK")
        if ok_meta:
            commands.append({**ok_meta, "allowed": True})
        return {"status": "ok", "commands": commands}

    @router.get("/hotkeys")
    async def get_hotkeys() -> Dict[str, Any]:
        try:
            from core.services.hotkey_map import get_hotkey_map

            return {"status": "ok", "hotkeys": get_hotkey_map()}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/ok/status")
    async def get_ok_status() -> Dict[str, Any]:
        status = _get_ok_local_status()
        cloud_status = _get_ok_cloud_status()
        config = _load_ai_modes_config()
        mode = (config.get("modes") or {}).get("ofvibe", {})
        declared_models = [m.get("name") for m in (mode.get("models") or []) if m.get("name")]
        default_models = mode.get("default_models") or {}
        logger.debug(
            "OK status requested",
            ctx={"model": status.get("model"), "ready": status.get("ready")},
        )
        return {
            "status": "ok",
            "ok": {
                **status,
                "context_window": _get_ok_context_window(),
                "default_model": _get_ok_default_model(),
                "default_models": default_models,
                "declared_models": declared_models,
                "cloud": cloud_status,
                "auto_fallback": _ok_auto_fallback_enabled(),
            },
        }

    @router.get("/ok/history")
    async def get_ok_history() -> Dict[str, Any]:
        return {"status": "ok", "history": list(ok_history)}

    class OkModelRequest(BaseModel):
        model: str
        profile: Optional[str] = "core"

    class OkCloudRequest(BaseModel):
        prompt: str
        mode: Optional[str] = "conversation"
        workspace: Optional[str] = "core"

    @router.post("/ok/model")
    async def set_ok_model(payload: OkModelRequest) -> Dict[str, Any]:
        model = (payload.model or "").strip()
        profile = (payload.profile or "core").strip().lower()
        if not model:
            logger.warn("OK model update rejected (empty)")
            raise HTTPException(status_code=400, detail="model is required")
        if profile not in {"core", "dev"}:
            logger.warn("OK model update rejected (invalid profile)", ctx={"profile": profile})
            raise HTTPException(status_code=400, detail="profile must be core or dev")

        config = _load_ai_modes_config()
        modes = config.setdefault("modes", {})
        ofvibe = modes.setdefault("ofvibe", {})
        default_models = ofvibe.setdefault("default_models", {})
        default_models[profile] = model

        models = ofvibe.setdefault("models", [])
        if model not in [m.get("name") for m in models if isinstance(m, dict)]:
            models.append({"name": model, "availability": [profile]})

        _write_ok_modes_config(config)
        logger.info("OK model updated", ctx={"model": model, "profile": profile})
        return {"status": "ok", "default_models": default_models}

    @router.post("/ok/cloud")
    async def run_ok_cloud(payload: OkCloudRequest) -> Dict[str, Any]:
        prompt = (payload.prompt or "").strip()
        if not prompt:
            raise HTTPException(status_code=400, detail="prompt is required")

        status = _get_ok_cloud_status()
        if not status.get("ready"):
            raise HTTPException(status_code=400, detail=status.get("issue") or "mistral unavailable")

        try:
            response, model = _run_ok_cloud(prompt)
        except Exception as exc:
            logger.warn("OK cloud request failed", ctx={"error": str(exc)})
            raise HTTPException(status_code=500, detail=str(exc))

        return {"status": "ok", "response": response, "model": model}

    @router.post("/ok/setup")
    async def run_ok_setup() -> Dict[str, Any]:
        try:
            from core.services.logging_api import get_repo_root
            from core.services.ok_setup import run_ok_setup as _run_ok_setup

            result = _run_ok_setup(get_repo_root())
            return {"status": "ok", "result": result}
        except Exception as exc:
            logger.warn("OK setup failed", ctx={"error": str(exc)})
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/user")
    async def get_current_user() -> Dict[str, Any]:
        try:
            from core.services.user_service import get_user_manager, is_ghost_mode

            user_mgr = get_user_manager()
            user = user_mgr.current()
            if not user:
                return {"status": "error", "message": "No current user"}
            return {
                "status": "ok",
                "user": user.to_dict(),
                "ghost_mode": is_ghost_mode(),
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/users")
    async def list_users() -> Dict[str, Any]:
        try:
            from core.services.user_service import get_user_manager

            user_mgr = get_user_manager()
            return {"status": "ok", "users": user_mgr.list_users()}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    class UserSwitchRequest(BaseModel):
        username: str

    class UserRoleRequest(BaseModel):
        username: str
        role: str

    @router.post("/user/switch")
    async def switch_user(payload: UserSwitchRequest) -> Dict[str, Any]:
        try:
            from core.services.user_service import get_user_manager

            user_mgr = get_user_manager()
            success, msg = user_mgr.switch_user(payload.username)
            if not success:
                raise HTTPException(status_code=400, detail=msg)
            return {"status": "ok", "message": msg}
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/user/role")
    async def set_user_role(payload: UserRoleRequest) -> Dict[str, Any]:
        try:
            from core.services.user_service import (
                get_user_manager,
                UserRole,
                Permission,
            )

            user_mgr = get_user_manager()
            if not user_mgr.has_permission(Permission.ADMIN):
                raise HTTPException(status_code=403, detail="Admin permission required")
            try:
                role = UserRole(payload.role.lower())
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid role")
            success, msg = user_mgr.set_role(payload.username, role)
            if not success:
                raise HTTPException(status_code=400, detail=msg)
            return {"status": "ok", "message": msg}
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.post("/dispatch")
    async def dispatch_command(payload: DispatchRequest) -> Dict[str, Any]:
        if not dispatcher:
            raise HTTPException(status_code=500, detail="uCODE dispatcher unavailable")

        corr_id = new_corr_id("C")
        token = set_corr_id(corr_id)
        try:
            command = (payload.command or "").strip()
            response = _dispatch_core(command, payload, corr_id)
            return response
        finally:
            reset_corr_id(token)

    def _extract_output(result: Dict[str, Any], rendered_text: Optional[str]) -> str:
        if result.get("output"):
            return result["output"]
        if result.get("help"):
            return result["help"]
        if result.get("text"):
            return result["text"]
        if result.get("message"):
            return result["message"]
        return rendered_text or ""

    def _dispatch_core(
        command: str, payload: DispatchRequest, corr_id: str
    ) -> Dict[str, Any]:
        if not command:
            logger.warn("Empty command rejected", ctx={"corr_id": corr_id})
            raise HTTPException(status_code=400, detail="command is required")

        # Normalize uCODE-style prefixes (case-insensitive)
        if command.startswith("?"):
            rest = command[1:].strip()
            command = f"OK {rest}".strip()
        upper = command.upper()
        if upper == "OK" or upper.startswith("OK "):
            ok_args = command[2:].strip()
            ok_tokens = ok_args.split() if ok_args else []
            ok_mode = (ok_tokens[0].upper() if ok_tokens else "LOCAL")
            if ok_mode in {"LOCAL", "VIBE"}:
                logger.info(
                    "OK local history request",
                    ctx={"corr_id": corr_id, "mode": ok_mode},
                )
                limit = 5
                if len(ok_tokens) >= 2 and ok_tokens[1].isdigit():
                    limit = max(1, int(ok_tokens[1]))
                entries = ok_history[-limit:] if ok_history else []
                return {
                    "status": "ok",
                    "command": command,
                    "result": {
                        "status": "success",
                        "message": "OK LOCAL history",
                        "output": "",
                    },
                    "ok_history": entries,
                }

            if ok_mode == "FALLBACK":
                toggle = ok_tokens[1].lower() if len(ok_tokens) > 1 else ""
                config = _load_ai_modes_config()
                modes = config.setdefault("modes", {})
                ofvibe = modes.setdefault("ofvibe", {})
                if toggle in {"on", "true", "yes"}:
                    ofvibe["auto_fallback"] = True
                    _write_ok_modes_config(config)
                    return {
                        "status": "ok",
                        "command": command,
                        "result": {
                            "status": "success",
                            "message": "OK fallback set to auto (on)",
                            "output": "",
                        },
                    }
                if toggle in {"off", "false", "no"}:
                    ofvibe["auto_fallback"] = False
                    _write_ok_modes_config(config)
                    return {
                        "status": "ok",
                        "command": command,
                        "result": {
                            "status": "success",
                            "message": "OK fallback set to manual (off)",
                            "output": "",
                        },
                    }
                current = "on" if _ok_auto_fallback_enabled() else "off"
                return {
                    "status": "ok",
                    "command": command,
                    "result": {
                        "status": "success",
                        "message": f"OK fallback is {current}",
                        "output": "Usage: OK FALLBACK on|off",
                    },
                }

            if ok_mode in {"EXPLAIN", "DIFF", "PATCH"}:
                parsed = _parse_ok_file_args(" ".join(ok_tokens[1:]))
                if parsed.get("error"):
                    logger.warn(
                        "OK command rejected",
                        ctx={"corr_id": corr_id, "error": parsed.get("error")},
                    )
                    raise HTTPException(status_code=400, detail=parsed.get("error"))
                path = parsed["path"]
                if not path.exists():
                    logger.warn(
                        "OK file missing",
                        ctx={"corr_id": corr_id, "path": str(path)},
                    )
                    raise HTTPException(status_code=404, detail=f"File not found: {path}")
                content = path.read_text(encoding="utf-8", errors="ignore")
                if parsed.get("line_start") and parsed.get("line_end"):
                    lines = content.splitlines()
                    content = "\n".join(
                        lines[parsed["line_start"] - 1 : parsed["line_end"]]
                    )
                if ok_mode == "EXPLAIN":
                    prompt = (
                        f"Explain this code from {path}:\n\n"
                        f"```python\n{content}\n```\n\n"
                        "Provide: 1) purpose, 2) key logic, 3) risks or follow-ups."
                    )
                elif ok_mode == "DIFF":
                    prompt = (
                        f"Propose a unified diff for improvements to {path}.\n\n"
                        f"```python\n{content}\n```\n\n"
                        "Return a unified diff only (no commentary)."
                    )
                else:
                    prompt = (
                        f"Draft a patch (unified diff) for {path}. Keep the diff minimal.\n\n"
                        f"```python\n{content}\n```\n\n"
                        "Return a unified diff only."
                    )

                model = payload.ok_model or _get_ok_default_model()
                source = "local"
                response_text = None
                auto_fallback = _ok_auto_fallback_enabled()

                if parsed.get("use_cloud"):
                    from wizard.services.mistral_api import MistralAPI
                    if not MistralAPI().available():
                        logger.warn(
                            "OK cloud rejected (missing Mistral key)",
                            ctx={"corr_id": corr_id},
                        )
                        raise HTTPException(status_code=400, detail="Mistral API key required for cloud OK")
                    try:
                        response_text, model = _run_ok_cloud(prompt)
                        source = "cloud"
                    except Exception:
                        response_text = None

                if response_text is None:
                    try:
                        response_text = _run_ok_local(prompt, model=model)
                    except Exception:
                        response_text = None
                        if auto_fallback and not parsed.get("use_cloud"):
                            from wizard.services.mistral_api import MistralAPI
                            if MistralAPI().available():
                                response_text, model = _run_ok_cloud(prompt)
                                source = "cloud"
                            else:
                                raise HTTPException(status_code=400, detail="Mistral API key required for cloud OK")
                        else:
                            raise HTTPException(status_code=500, detail="OK local failed")

                entry = _record_ok_output(
                    prompt=prompt,
                    response=response_text,
                    model=model,
                    source=source,
                    mode=ok_mode,
                    file_path=str(path),
                )
                logger.info(
                    "OK command completed",
                    ctx={
                        "corr_id": corr_id,
                        "mode": ok_mode,
                        "model": model,
                        "source": source,
                        "file": str(path),
                    },
                )
                return {
                    "status": "ok",
                    "command": command,
                    "result": {
                        "status": "success",
                        "message": f"OK {ok_mode} complete",
                        "output": response_text,
                    },
                    "ok": entry,
                }

            # Default: treat OK <prompt> as a local AI request (parity with uCODE TUI).
            prompt = ok_args.strip()
            if not prompt:
                logger.warn("OK command not recognized", ctx={"corr_id": corr_id, "mode": ok_mode})
                raise HTTPException(status_code=400, detail="OK command not recognized")

            model = payload.ok_model or _get_ok_default_model()
            source = "local"
            response_text = None
            auto_fallback = _ok_auto_fallback_enabled()
            try:
                response_text = _run_ok_local(prompt, model=model)
            except Exception as exc:
                if auto_fallback:
                    from wizard.services.mistral_api import MistralAPI
                    if not MistralAPI().available():
                        logger.warn(
                            "OK cloud rejected (missing Mistral key)",
                            ctx={"corr_id": corr_id},
                        )
                        raise HTTPException(status_code=400, detail="Mistral API key required for cloud OK")
                    response_text, model = _run_ok_cloud(prompt)
                    source = "cloud"
                else:
                    logger.warn(
                        "OK prompt failed",
                        ctx={"corr_id": corr_id, "mode": ok_mode, "error": str(exc)},
                    )
                    raise HTTPException(status_code=500, detail="OK prompt failed")

            entry = _record_ok_output(
                prompt=prompt,
                response=response_text,
                model=model,
                source=source,
                mode="LOCAL",
                file_path=None,
            )
            logger.info(
                "OK prompt completed",
                ctx={"corr_id": corr_id, "model": model, "source": source},
            )
            return {
                "status": "ok",
                "command": command,
                "result": {
                    "status": "success",
                    "message": "OK prompt complete",
                    "output": response_text,
                },
                "ok": entry,
            }

        # Slash-prefixed command: uCODE first, then shell
        if command.startswith("/"):
            slash_cmd = command[1:].strip()
            first_token = slash_cmd.split()[0].upper() if slash_cmd else ""
            if first_token in allowlist:
                command = slash_cmd
            else:
                if not _shell_allowed():
                    logger.warn("Shell command blocked", ctx={"corr_id": corr_id})
                    raise HTTPException(status_code=403, detail="shell commands disabled")
                shell_cmd = slash_cmd
                if not shell_cmd:
                    logger.warn("Shell command rejected (empty)", ctx={"corr_id": corr_id})
                    raise HTTPException(status_code=400, detail="shell command is required")
                if not _shell_safe(shell_cmd):
                    logger.warn(
                        "Shell command failed safety check",
                        ctx={"corr_id": corr_id, "command": shell_cmd},
                    )
                    raise HTTPException(status_code=403, detail="shell command blocked (destructive)")
                try:
                    logger.info(
                        "Shell command dispatch",
                        ctx={"corr_id": corr_id, "command": shell_cmd},
                    )
                    result = subprocess.run(
                        shell_cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                except subprocess.TimeoutExpired:
                    logger.warn("Shell command timeout", ctx={"corr_id": corr_id})
                    raise HTTPException(status_code=408, detail="shell command timed out")
                output = result.stdout or result.stderr
                return {
                    "status": "ok",
                    "command": f"/{shell_cmd}",
                    "result": {
                        "status": "success" if result.returncode == 0 else "error",
                        "message": output or f"exit code {result.returncode}",
                        "shell_output": output,
                        "exit_code": result.returncode,
                    },
                }

        cmd_name = command.split()[0].upper()
        if cmd_name == "SETUP" and len(command.split()) == 1:
            story_state = _load_setup_story()
            logger.info("Setup story served", ctx={"corr_id": corr_id})
            return {
                "status": "ok",
                "command": command,
                "result": {
                    "status": "success",
                    "message": "Setup story ready",
                    "frontmatter": story_state.get("frontmatter"),
                    "sections": story_state.get("sections"),
                },
            }
        if cmd_name not in allowlist:
            logger.warn(
                "Command blocked by allowlist",
                ctx={"corr_id": corr_id, "command": cmd_name},
            )
            raise HTTPException(status_code=403, detail=f"command not allowed: {cmd_name}")

        logger.info(
            "Dispatch command",
            ctx={"corr_id": corr_id, "command": cmd_name, "raw": command},
        )
        result = dispatcher.dispatch(command, game_state=game_state)
        logger.info(
            "Dispatch result",
            ctx={"corr_id": corr_id, "status": result.get("status") if isinstance(result, dict) else None},
        )
        response: Dict[str, Any] = {
            "status": "ok",
            "command": command,
            "result": result,
        }
        if renderer:
            try:
                response["rendered"] = renderer.render(result)
            except Exception:
                pass
        return response

    @router.post("/dispatch/stream")
    async def dispatch_command_stream(payload: DispatchRequest) -> StreamingResponse:
        if not dispatcher:
            raise HTTPException(status_code=500, detail="uCODE dispatcher unavailable")

        corr_id = new_corr_id("C")
        token = set_corr_id(corr_id)
        command = (payload.command or "").strip()
        if not command:
            logger.warn("Empty stream command rejected", ctx={"corr_id": corr_id})
            reset_corr_id(token)
            raise HTTPException(status_code=400, detail="command is required")

        def _sse(event: str, data: Dict[str, Any]) -> bytes:
            payload_text = json.dumps(data)
            return f"event: {event}\ndata: {payload_text}\n\n".encode("utf-8")

        def _stream_chunks(text: str) -> Generator[bytes, None, None]:
            if text is None:
                return
            if "\n" in text:
                lines = text.splitlines()
                for idx, line in enumerate(lines):
                    suffix = "\n" if idx < len(lines) - 1 else ""
                    yield _sse("chunk", {"text": f"{line}{suffix}"})
            else:
                yield _sse("chunk", {"text": text})

        async def event_stream() -> Generator[bytes, None, None]:
            yield _sse("start", {"command": command})
            try:
                logger.info(
                    "Stream dispatch",
                    ctx={"corr_id": corr_id, "raw": command},
                )
                working_command = command
                if working_command.startswith("?"):
                    rest = working_command[1:].strip()
                    working_command = f"OK {rest}".strip()
                upper = working_command.upper()
                if upper == "OK" or upper.startswith("OK "):
                    ok_args = working_command[2:].strip()
                    ok_tokens = ok_args.split() if ok_args else []
                    ok_mode = (ok_tokens[0].upper() if ok_tokens else "LOCAL")
                    if ok_mode in {"EXPLAIN", "DIFF", "PATCH"}:
                        parsed = _parse_ok_file_args(" ".join(ok_tokens[1:]))
                        if parsed.get("error"):
                            logger.warn(
                                "OK stream rejected",
                                ctx={"corr_id": corr_id, "error": parsed.get("error")},
                            )
                            raise HTTPException(status_code=400, detail=parsed.get("error"))
                        path = parsed["path"]
                        if not path.exists():
                            logger.warn(
                                "OK stream file missing",
                                ctx={"corr_id": corr_id, "path": str(path)},
                            )
                            raise HTTPException(status_code=404, detail=f"File not found: {path}")
                        content = path.read_text(encoding="utf-8", errors="ignore")
                        if parsed.get("line_start") and parsed.get("line_end"):
                            lines = content.splitlines()
                            content = "\n".join(
                                lines[parsed["line_start"] - 1 : parsed["line_end"]]
                            )
                        if ok_mode == "EXPLAIN":
                            prompt = (
                                f"Explain this code from {path}:\n\n"
                                f"```python\n{content}\n```\n\n"
                                "Provide: 1) purpose, 2) key logic, 3) risks or follow-ups."
                            )
                        elif ok_mode == "DIFF":
                            prompt = (
                                f"Propose a unified diff for improvements to {path}.\n\n"
                                f"```python\n{content}\n```\n\n"
                                "Return a unified diff only (no commentary)."
                            )
                        else:
                            prompt = (
                                f"Draft a patch (unified diff) for {path}. Keep the diff minimal.\n\n"
                                f"```python\n{content}\n```\n\n"
                                "Return a unified diff only."
                            )

                        model = payload.ok_model or _get_ok_default_model()
                        source = "local"
                        response_text = ""
                        auto_fallback = _ok_auto_fallback_enabled()

                        if parsed.get("use_cloud"):
                            try:
                                response_text, model = _run_ok_cloud(prompt)
                                source = "cloud"
                                for chunk in _stream_chunks(response_text):
                                    yield chunk
                            except Exception:
                                response_text = ""

                        if not response_text:
                            from wizard.services.vibe_service import VibeService, VibeConfig

                            config = VibeConfig(model=model)
                            vibe = VibeService(config=config)
                            try:
                                stream = vibe.generate(prompt, format="markdown", stream=True)
                                buffer = ""
                                for part in stream:
                                    buffer += part
                                    yield _sse("chunk", {"text": part})
                                response_text = buffer
                            except Exception:
                                response_text = ""

                        if not response_text and auto_fallback:
                            from wizard.services.mistral_api import MistralAPI
                            if not MistralAPI().available():
                                raise HTTPException(status_code=400, detail="Mistral API key required for cloud OK")
                            response_text, model = _run_ok_cloud(prompt)
                            source = "cloud"
                            for chunk in _stream_chunks(response_text):
                                yield chunk

                        entry = _record_ok_output(
                            prompt=prompt,
                            response=response_text,
                            model=model,
                            source=source,
                            mode=ok_mode,
                            file_path=str(path),
                        )
                        response = {
                            "status": "ok",
                            "command": working_command,
                            "result": {
                                "status": "success",
                                "message": f"OK {ok_mode} complete",
                                "output": response_text,
                            },
                            "ok": entry,
                        }
                        yield _sse("result", response)
                        return
                response = _dispatch_core(command, payload, corr_id)
                rendered_text = response.get("rendered")
                output_text = _extract_output(response.get("result") or {}, rendered_text)
                for chunk in _stream_chunks(output_text):
                    yield chunk
                yield _sse("result", response)
            except HTTPException as exc:
                yield _sse("error", {"error": exc.detail})
            except Exception as exc:
                yield _sse("error", {"error": str(exc)})
            finally:
                reset_corr_id(token)

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    return router
