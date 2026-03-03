"""v1.5 Logic Assist setup helper for local contributor tooling."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

from core.services.template_workspace_service import get_template_workspace_service


def _default_logger(message: str) -> None:
    print(message)


def run_logic_assist_setup(
    repo_root: Path,
    log: Callable[[str], None] | None = None,
) -> dict[str, list[str]]:
    """Prepare the local GPT4All logic-assist lane and contributor CLI tooling."""
    logger = log or _default_logger
    steps: list[str] = []
    warnings: list[str] = []
    workspace = get_template_workspace_service(repo_root)
    snapshot = workspace.read_document("settings", "logic-assist")
    fields = workspace.parse_fields(str(snapshot.get("effective_content") or ""))
    local_model_path = fields.get("local_model_path", "memory/models/gpt4all")
    local_model_name = fields.get(
        "local_model_name", "mistral-7b-instruct-v0.2.Q4_0.gguf"
    )
    local_runtime = fields.get("local_runtime", "gpt4all")

    def run_cmd(cmd: list[str], label: str) -> bool:
        logger(f"  • {label}")
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception as exc:
            warnings.append(f"{label} failed: {exc}")
            return False
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "").strip()
            warnings.append(f"{label} failed: {detail or f'exit {proc.returncode}'}")
            return False
        steps.append(label)
        return True

    if shutil.which("uv"):
        run_cmd(["uv", "pip", "install", "gpt4all", "mistral-vibe"], "Install GPT4All and Vibe CLI")
    else:
        run_cmd([sys.executable, "-m", "pip", "install", "gpt4all", "mistral-vibe"], "Install GPT4All and Vibe CLI")

    model_dir = Path(local_model_path)
    if not model_dir.is_absolute():
        model_dir = repo_root / model_dir
    model_dir.mkdir(parents=True, exist_ok=True)
    steps.append(f"Prepared logic model directory: {model_dir}")

    model_file = model_dir / local_model_name
    if not model_file.exists():
        guidance_path = model_dir / "README.md"
        guidance_path.write_text(
            "\n".join(
                [
                    "# GPT4All Local Model",
                    "",
                    "Place the configured GPT4All model file in this folder.",
                    "",
                    f"- Expected file: `{local_model_name}`",
                    f"- Runtime: `{local_runtime}`",
                    "",
                    "The v1.5 local logic-assist runtime does not auto-download model files.",
                    "Wizard network escalation remains optional and separately budgeted.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        warnings.append(
            f"Model file missing: {model_file.name}. Added guidance at {guidance_path.relative_to(repo_root)}"
        )
    else:
        steps.append(f"Detected local GPT4All model: {model_file.name}")

    return {"steps": steps, "warnings": warnings}
