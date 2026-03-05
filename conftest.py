from __future__ import annotations

import os
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent
os.environ["UDOS_ROOT"] = str(_REPO_ROOT)
os.environ.setdefault("UDOS_ROOT_REQUIRED", "1")


def _normalize_item_path(item: object) -> None:
    path_value = getattr(item, "path", None)
    if isinstance(path_value, str):
        setattr(item, "path", Path(path_value))


def pytest_runtest_setup(item: pytest.Item) -> None:
    _normalize_item_path(item)


@pytest.fixture(autouse=True)
def _normalize_request_node_path(request: pytest.FixtureRequest) -> None:
    _normalize_item_path(request.node)
    os.environ["UDOS_ROOT"] = str(_REPO_ROOT)
