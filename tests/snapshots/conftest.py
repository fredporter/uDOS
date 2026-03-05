from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _pin_banner_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "vibe.cli.textual_ui.widgets.banner.banner.__version__", "0.0.0"
    )


@pytest.fixture(autouse=True)
def _normalize_request_node_path(request: pytest.FixtureRequest) -> None:
    """Compatibility shim for pytest node path shape across plugin versions."""
    node = request.node
    path_value = getattr(node, "path", None)
    if isinstance(path_value, str):
        setattr(node, "path", Path(path_value))
