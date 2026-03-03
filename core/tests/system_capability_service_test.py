from __future__ import annotations

from pathlib import Path

from core.services.system_capability_service import (
    MinimumSystemSpec,
    SystemCapabilityService,
)


def test_system_capability_service_evaluates_minimum_spec(monkeypatch, tmp_path: Path):
    service = SystemCapabilityService(tmp_path)
    monkeypatch.setattr(
        service,
        "measure",
        lambda: type(
            "Capability",
            (),
            {
                "hostname": "box",
                "system": "Linux",
                "release": "6.1",
                "arch": "x86_64",
                "processor": "amd64",
                "cpu_cores": 8,
                "ram_gb": 16.0,
                "storage_free_gb": 128.0,
                "storage_total_gb": 512.0,
                "uefi_native": True,
                "headless": False,
            },
        )(),
    )

    capability, result = service.evaluate_minimum_spec(
        MinimumSystemSpec(cpu_cores=4, ram_gb=8.0, storage_free_gb=20.0)
    )

    assert capability.cpu_cores == 8
    assert result.overall is True
    assert result.cpu is True
    assert result.ram is True
    assert result.storage is True


def test_system_capability_service_measure_returns_local_shape(tmp_path: Path):
    service = SystemCapabilityService(tmp_path)
    capability = service.measure()

    assert capability.cpu_cores >= 1
    assert capability.ram_gb >= 0.0
    assert capability.storage_total_gb >= 0.0
    assert isinstance(capability.uefi_native, bool)
    assert isinstance(capability.headless, bool)
