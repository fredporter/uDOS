from __future__ import annotations

import importlib.util
import inspect
import pickle
from pathlib import Path, PurePath
import sys
from typing import Any, Awaitable, Callable, Iterable

import pytest
from rich.console import Console
from syrupy import SnapshotAssertion
from textual.app import App


_THIS_FILE = Path(__file__).resolve()
_UPSTREAM = None
for _entry in sys.path:
    try:
        _candidate = (Path(_entry) / "pytest_textual_snapshot.py").resolve()
    except Exception:
        continue
    if _candidate == _THIS_FILE or not _candidate.exists():
        continue
    _spec = importlib.util.spec_from_file_location("_pytest_textual_snapshot_upstream", _candidate)
    if _spec and _spec.loader:
        _UPSTREAM = importlib.util.module_from_spec(_spec)
        sys.modules["_pytest_textual_snapshot_upstream"] = _UPSTREAM
        _spec.loader.exec_module(_UPSTREAM)
        break

if _UPSTREAM is None:
    raise ImportError("Unable to load upstream pytest_textual_snapshot module")

for _name in dir(_UPSTREAM):
    if _name.startswith("__"):
        continue
    globals()[_name] = getattr(_UPSTREAM, _name)


def node_to_report_path(node: Any) -> Path:
    """Generate a report file name for a test node with robust path coercion."""
    tempdir = get_tempdir()
    path, _, name = node.reportinfo()
    path_obj = Path(path) if isinstance(path, str) else path
    temp = path_obj.parent
    base: list[str] = []
    while temp != temp.parent and temp.name != "tests":
        base.append(temp.name)
        temp = temp.parent
    parts: list[str] = []
    if base:
        parts.append("_".join(reversed(base)))
    parts.append(path_obj.name.replace(".", "_"))
    parts.append(name.replace("[", "_").replace("]", "_"))
    return Path(tempdir.name) / "_".join(parts)


@pytest.fixture
def snap_compare(
    snapshot: SnapshotAssertion, request: pytest.FixtureRequest
) -> Callable[[str | PurePath], bool]:
    """Compatibility wrapper around upstream fixture for pytest node path drift."""
    snapshot = snapshot.use_extension(SVGImageExtension)

    def compare(
        app: str | PurePath | App[Any],
        press: Iterable[str] = (),
        terminal_size: tuple[int, int] = (80, 24),
        run_before: Callable[[Any], Awaitable[None] | None] | None = None,
    ) -> bool:
        from textual._import_app import import_app

        node = request.node

        if isinstance(app, App):
            app_instance = app
            app_path = ""
        else:
            path = Path(app)
            if path.is_absolute():
                app_path = str(path.resolve())
                app_instance = import_app(app_path)
            else:
                node_path = getattr(node, "path", None)
                if isinstance(node_path, str):
                    node_path = Path(node_path)
                if node_path is None:
                    full_path, _, _ = node.reportinfo()
                    node_path = Path(full_path)
                resolved = (node_path.parent / app).resolve()
                app_path = str(resolved)
                app_instance = import_app(app_path)

        from textual._doc import take_svg_screenshot

        actual_screenshot = take_svg_screenshot(
            app=app_instance,
            press=press,
            terminal_size=terminal_size,
            run_before=run_before,
        )
        console = Console(legacy_windows=False, force_terminal=True)
        p_app = PseudoApp(PseudoConsole(console.legacy_windows, console.size))

        result = snapshot == actual_screenshot

        execution_index = (
            snapshot._custom_index
            and snapshot._execution_name_index.get(snapshot._custom_index)
        ) or snapshot.num_executions - 1
        assertion_result = snapshot.executions.get(execution_index)

        snapshot_exists = (
            execution_index in snapshot.executions
            and assertion_result
            and assertion_result.final_data is not None
        )

        expected_svg_text = str(snapshot)
        full_path, line_number, name = node.reportinfo()

        data = (
            result,
            expected_svg_text,
            actual_screenshot,
            p_app,
            full_path,
            line_number,
            name,
            inspect.getdoc(node.function) or "",
            app_path,
            snapshot_exists,
        )
        data_path = node_to_report_path(request.node)
        data_path.write_bytes(pickle.dumps(data))

        return result

    return compare
