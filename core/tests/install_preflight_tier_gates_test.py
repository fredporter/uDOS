from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER = REPO_ROOT / "bin" / "install-udos-vibe.sh"


def _run_preflight(*, tier: str, probes: dict[str, str]) -> dict[str, object]:
    env = os.environ.copy()
    env.update(probes)
    proc = subprocess.run(
        ["bash", str(INSTALLER), "--preflight-json", "--tier", tier],
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr

    lines = proc.stdout.splitlines()
    json_start = next((idx for idx, line in enumerate(lines) if line.strip().startswith("{")), None)
    assert json_start is not None, proc.stdout
    payload = "\n".join(lines[json_start:])
    return json.loads(payload)


def test_preflight_blocks_local_tier_on_legacy_platform() -> None:
    result = _run_preflight(
        tier="2",
        probes={
            "UDOS_INSTALLER_PROBE_OS_TYPE": "mac",
            "UDOS_INSTALLER_PROBE_OS_VERSION": "10.14",
            "UDOS_INSTALLER_PROBE_CPU_CORES": "8",
            "UDOS_INSTALLER_PROBE_RAM_GB": "16",
            "UDOS_INSTALLER_PROBE_FREE_STORAGE_GB": "100",
            "UDOS_INSTALLER_PROBE_HAS_GPU": "1",
            "UDOS_INSTALLER_PROBE_GPU_VRAM_GB": "8",
        },
    )
    assert result["selected_tier"] == "tier1"
    assert result["local_models_allowed"] is False
    assert result["block_reason"] == "legacy_platform"


def test_preflight_blocks_tier2_when_resources_are_insufficient() -> None:
    result = _run_preflight(
        tier="2",
        probes={
            "UDOS_INSTALLER_PROBE_OS_TYPE": "ubuntu",
            "UDOS_INSTALLER_PROBE_OS_VERSION": "24.04",
            "UDOS_INSTALLER_PROBE_KERNEL_VERSION": "6.8.0",
            "UDOS_INSTALLER_PROBE_CPU_CORES": "2",
            "UDOS_INSTALLER_PROBE_RAM_GB": "4",
            "UDOS_INSTALLER_PROBE_FREE_STORAGE_GB": "20",
            "UDOS_INSTALLER_PROBE_HAS_GPU": "0",
        },
    )
    assert result["selected_tier"] == "tier1"
    assert result["local_models_allowed"] is False
    assert result["block_reason"] == "insufficient_resources"


def test_preflight_auto_selects_tier2_for_supported_host() -> None:
    result = _run_preflight(
        tier="auto",
        probes={
            "UDOS_INSTALLER_PROBE_OS_TYPE": "ubuntu",
            "UDOS_INSTALLER_PROBE_OS_VERSION": "24.04",
            "UDOS_INSTALLER_PROBE_KERNEL_VERSION": "6.8.0",
            "UDOS_INSTALLER_PROBE_CPU_CORES": "6",
            "UDOS_INSTALLER_PROBE_RAM_GB": "12",
            "UDOS_INSTALLER_PROBE_FREE_STORAGE_GB": "40",
            "UDOS_INSTALLER_PROBE_HAS_GPU": "0",
        },
    )
    assert result["auto_tier"] == "tier2"
    assert result["selected_tier"] == "tier2"
    assert result["local_models_allowed"] is True
    assert result["local_recommended_models"] == [
        "devstral-small-2",
        "mistral",
        "llama3.2",
        "qwen3",
    ]


def test_preflight_auto_selects_tier3_for_gpu_host_with_vram() -> None:
    result = _run_preflight(
        tier="auto",
        probes={
            "UDOS_INSTALLER_PROBE_OS_TYPE": "ubuntu",
            "UDOS_INSTALLER_PROBE_OS_VERSION": "24.04",
            "UDOS_INSTALLER_PROBE_KERNEL_VERSION": "6.8.0",
            "UDOS_INSTALLER_PROBE_CPU_CORES": "12",
            "UDOS_INSTALLER_PROBE_RAM_GB": "32",
            "UDOS_INSTALLER_PROBE_FREE_STORAGE_GB": "120",
            "UDOS_INSTALLER_PROBE_HAS_GPU": "1",
            "UDOS_INSTALLER_PROBE_GPU_VRAM_GB": "12",
        },
    )
    assert result["auto_tier"] == "tier3"
    assert result["selected_tier"] == "tier3"
    assert result["local_models_allowed"] is True
    assert result["local_recommended_models"] == [
        "mistral",
        "devstral-small-2",
        "llama3.2",
        "qwen3",
        "codellama",
        "phi3",
        "gemma2",
        "deepseek-coder",
    ]
