"""Contract checks for core networking boundaries."""

from __future__ import annotations

import ast
from pathlib import Path
from urllib.parse import urlparse

_NETWORK_IMPORT_ROOTS = frozenset({"requests", "httpx", "aiohttp", "socket", "urllib", "websockets"})
_CORE_ROOT = Path("core")
_SKIP_PARTS = frozenset({"tests", "examples", "grid-runtime"})
_NETWORK_ALLOWLIST = frozenset(
    {
        Path("core/commands/wizard_handler.py"),
        Path("core/services/config_sync_service.py"),
        Path("core/services/dev_state.py"),
        Path("core/services/network_gate_policy.py"),
        Path("core/services/ok_setup.py"),
        Path("core/services/self_healer.py"),
        Path("core/services/stdlib_http.py"),
        Path("core/services/dev_mode_compat/network_service.py"),
        Path("core/services/wizard_proxy_service.py"),
        Path("core/tui/fkey_handler.py"),
        Path("core/tui/status_bar.py"),
        Path("core/tui/ucode.py"),
    }
)
_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})
_HTTP_HELPER_NAMES = frozenset({"http_get", "http_post", "http_put", "http_delete"})
_HTTP_METHOD_NAMES = frozenset({"get", "post", "put", "delete", "urlopen"})
_SOCKET_METHOD_NAMES = frozenset({"connect", "connect_ex", "create_connection"})


def _iter_core_python_files() -> list[Path]:
    return [
        path
        for path in _CORE_ROOT.rglob("*.py")
        if not any(part in _SKIP_PARTS for part in path.parts)
    ]


def _network_import_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        match node:
            case ast.Import(names=names):
                imports.update(alias.name.split(".", 1)[0] for alias in names)
            case ast.ImportFrom(module=module) if module:
                imports.add(module.split(".", 1)[0])
            case _:
                continue
    return imports & _NETWORK_IMPORT_ROOTS


def _literal_str(node: ast.AST) -> str | None:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _loopback_host(host: str | None) -> bool:
    return (host or "").strip().lower() in _LOOPBACK_HOSTS


def _literal_http_host(node: ast.AST) -> str | None:
    if not (url := _literal_str(node)):
        return None
    if not (url.startswith("http://") or url.startswith("https://")):
        return None
    parsed = urlparse(url)
    return (parsed.hostname or "").strip().lower() or None


def _literal_socket_host(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Tuple) or not node.elts:
        return None
    return (_literal_str(node.elts[0]) or "").strip().lower() or None


def _literal_non_loopback_targets(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    violations: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        host: str | None = None
        call_name = ""
        fn = node.func

        match fn:
            case ast.Name(id=name) if name in _HTTP_HELPER_NAMES:
                call_name = name
                if node.args:
                    host = _literal_http_host(node.args[0])
            case ast.Attribute(attr=attr, value=value) if attr in _HTTP_METHOD_NAMES:
                call_name = attr
                if node.args:
                    if attr == "urlopen":
                        first = node.args[0]
                        if isinstance(first, ast.Call) and first.args:
                            host = _literal_http_host(first.args[0])
                        else:
                            host = _literal_http_host(first)
                    elif isinstance(value, ast.Name) and value.id == "requests":
                        host = _literal_http_host(node.args[0])
            case ast.Attribute(attr=attr) if attr in _SOCKET_METHOD_NAMES:
                call_name = attr
                if node.args:
                    host = _literal_socket_host(node.args[0])
            case _:
                continue

        if host and not _loopback_host(host):
            violations.append(f"{path}:{node.lineno}:{call_name}:{host}")

    return violations


def test_core_network_imports_do_not_expand_outside_allowlist() -> None:
    violating_files = sorted(
        str(path)
        for path in _iter_core_python_files()
        if _network_import_roots(path) and path not in _NETWORK_ALLOWLIST
    )
    assert not violating_files, f"Unexpected core network imports: {violating_files}"


def test_core_tui_has_no_public_dns_probe() -> None:
    assert "1.1.1.1" not in Path("core/tui/ucode.py").read_text(encoding="utf-8")


def test_core_literal_network_targets_are_loopback_only() -> None:
    violations: list[str] = []
    for path in _iter_core_python_files():
        if path in _NETWORK_ALLOWLIST:
            violations.extend(_literal_non_loopback_targets(path))
    assert not violations, f"Non-loopback literal network targets: {violations}"
