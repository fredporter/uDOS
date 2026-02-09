"""Version string for setuptools/pyproject.toml dynamic version resolution."""

import json
from pathlib import Path

_version_file = Path(__file__).parent / "version.json"
try:
    with open(_version_file) as f:
        _data = json.load(f)
    _v = _data["version"]
    VERSION = f"{_v['major']}.{_v['minor']}.{_v['patch']}"
except (FileNotFoundError, KeyError, json.JSONDecodeError):
    VERSION = "0.0.0"
