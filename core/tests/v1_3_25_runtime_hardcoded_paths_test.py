from pathlib import Path

from tools.ci.check_v1_3_25_runtime_hardcoded_paths import HARD_PATH_RE


def test_runtime_hardcoded_path_regex_flags_local_machine_paths():
    assert HARD_PATH_RE.search("/Users/fredbook/Code/uDOS")
    assert HARD_PATH_RE.search("C:/Users/Fred/Desktop")
    assert HARD_PATH_RE.search(r"C:\\Users\\Fred\\Desktop")


def test_runtime_hardcoded_path_regex_ignores_relative_paths():
    assert not HARD_PATH_RE.search("memory/reports/file.json")
    assert not HARD_PATH_RE.search("./core/services/gameplay_service.py")


def test_runtime_hardcoded_path_regex_scan_line_numbers():
    lines = [
        "alpha",
        "path=/Users/example/project",
        "beta",
    ]
    matches = [idx for idx, line in enumerate(lines, start=1) if HARD_PATH_RE.search(line)]
    assert matches == [2]
