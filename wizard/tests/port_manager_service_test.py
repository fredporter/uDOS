from __future__ import annotations

from pathlib import Path

from wizard.services.port_manager import PortManager, Service, ServiceEnvironment, ServiceStatus


def test_check_service_port_treats_python3_as_python(tmp_path: Path) -> None:
    manager = PortManager(config_path=tmp_path / "port_registry.json")
    manager.services = {
        "wizard": Service(
            name="wizard",
            port=8765,
            environment=ServiceEnvironment.PRODUCTION,
            process_name="python",
        )
    }
    manager.is_port_open = lambda _port: False
    manager.get_port_occupant = lambda _port: {"pid": 777, "process": "python3", "port": 8765}

    status = manager.check_service_port("wizard")

    assert status == ServiceStatus.RUNNING
    assert manager.services["wizard"].pid == 777


def test_get_conflicts_ignores_node_for_npm_service(tmp_path: Path) -> None:
    manager = PortManager(config_path=tmp_path / "port_registry.json")
    manager.services = {
        "vite": Service(
            name="vite",
            port=5173,
            environment=ServiceEnvironment.DEVELOPMENT,
            process_name="npm",
        )
    }
    manager.get_port_occupant = lambda _port: {"pid": 888, "process": "node", "port": 5173}

    conflicts = manager.get_conflicts()

    assert conflicts == []


def test_get_available_port_skips_reserved_and_registered(tmp_path: Path) -> None:
    manager = PortManager(config_path=tmp_path / "port_registry.json")
    manager.services = {
        "wizard": Service(
            name="wizard",
            port=8765,
            environment=ServiceEnvironment.PRODUCTION,
            process_name="python",
        ),
        "vite": Service(
            name="vite",
            port=5173,
            environment=ServiceEnvironment.DEVELOPMENT,
            process_name="npm",
        ),
    }
    manager.is_port_open = lambda port: port in {9000, 9001, 9002}

    port = manager.get_available_port(start_port=9000, reserved_ports={9000, 9001})

    assert port == 9002
