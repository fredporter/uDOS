import json
from types import SimpleNamespace

from wizard.services.library_manager_service import LibraryManagerService


def _integration(name, path, installed=False):
    return SimpleNamespace(
        name=name,
        path=str(path),
        source="library",
        has_container=True,
        version="1.0.0",
        description=name,
        installed=installed,
        enabled=False,
        can_install=True,
    )


def test_resolve_integration_dependencies(tmp_path, monkeypatch):
    manager = LibraryManagerService(tmp_path)
    a_path = tmp_path / "library" / "a"
    b_path = tmp_path / "library" / "b"
    a_path.mkdir(parents=True)
    b_path.mkdir(parents=True)
    (a_path / "container.json").write_text(
        json.dumps({"dependencies": {"integrations": ["b", "missing"], "apk_dependencies": ["bash"]}}),
        encoding="utf-8",
    )
    (b_path / "container.json").write_text(json.dumps({}), encoding="utf-8")

    a = _integration("a", a_path)
    b = _integration("b", b_path)
    integrations = {"a": a, "b": b}

    monkeypatch.setattr(
        manager,
        "get_library_status",
        lambda: SimpleNamespace(integrations=[a, b]),
    )
    monkeypatch.setattr(manager, "get_integration", lambda name: integrations.get(name))

    payload = manager.resolve_integration_dependencies("a")
    assert payload["found"] is True
    assert payload["direct_integrations"] == ["b", "missing"]
    assert payload["install_order"] == ["b"]
    assert payload["missing_integrations"] == ["missing"]
    assert payload["package_dependencies"]["apk_dependencies"] == []


def test_install_integration_installs_dependencies_first(tmp_path, monkeypatch):
    manager = LibraryManagerService(tmp_path)
    a_path = tmp_path / "library" / "a"
    b_path = tmp_path / "library" / "b"
    a_path.mkdir(parents=True)
    b_path.mkdir(parents=True)
    (a_path / "container.json").write_text(
        json.dumps({"dependencies": {"integrations": ["b"]}}),
        encoding="utf-8",
    )
    (b_path / "container.json").write_text(json.dumps({}), encoding="utf-8")

    a = _integration("a", a_path, installed=False)
    b = _integration("b", b_path, installed=False)
    integrations = {"a": a, "b": b}

    monkeypatch.setattr(
        manager,
        "get_library_status",
        lambda: SimpleNamespace(integrations=[a, b]),
    )
    monkeypatch.setattr(manager, "get_integration", lambda name: integrations.get(name))
    monkeypatch.setattr(manager, "_run_setup_script", lambda _path: (True, "ok"))

    def _install_pm(name, _path):
        integrations[name].installed = True
        return True, "ok"

    monkeypatch.setattr(manager, "_install_via_package_manager", _install_pm)

    result = manager.install_integration("a")
    assert result.success is True
    assert a.installed is True
    assert b.installed is True
