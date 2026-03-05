from __future__ import annotations

from pathlib import Path

import pytest


def _normalize_item_path(item: object) -> None:
    path_value = getattr(item, "path", None)
    if isinstance(path_value, str):
        setattr(item, "path", Path(path_value))


def pytest_runtest_setup(item: pytest.Item) -> None:
    _normalize_item_path(item)


@pytest.fixture(autouse=True)
def _normalize_request_node_path(request: pytest.FixtureRequest) -> None:
    _normalize_item_path(request.node)
