"""
Path Migration Script - Phase 3

Audits and updates hardcoded memory/ paths to use FHS-compliant path helpers.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Path migration mapping
# Old path -> New path helper call
PATH_MIGRATIONS = {
    # Logs
    'Path("memory/logs")': 'get_user_path("logs")',
    "Path('memory/logs')": 'get_user_path("logs")',
    '"memory/logs"': 'str(get_user_path("logs"))',
    "'memory/logs'": 'str(get_user_path("logs"))',
    # Config directories
    'Path("memory/bank/user")': 'get_user_path("bank/user")',
    "Path('memory/bank/user')": 'get_user_path("bank/user")',
    # Sandbox
    'Path("memory/sandbox")': 'get_user_path("sandbox")',
    "Path('memory/sandbox')": 'get_user_path("sandbox")',
    'Path("memory/ucode")': 'get_user_path("ucode")',
    'Path("memory/workflows")': 'get_user_path("workflows")',
    # Common files
    'Path("memory/bank/user/user-state.json")': 'get_user_path("bank/user/user-state.json")',
    'Path("memory/bank/user/variables.json")': 'get_user_path("bank/user/variables.json")',
    'Path("memory/bank/system/device.json")': 'get_user_path("bank/system/device.json")',
}

# Files to update
TARGET_FILES = [
    "core/services/state_manager.py",
    "core/services/device_manager.py",
    "core/services/log_compression.py",
    "core/services/debug_panel_service.py",
    "core/services/unified_task_manager.py",
    "core/udos_core.py",
]


def analyze_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """
    Analyze file for hardcoded paths.

    Returns:
        List of (line_number, old_code, suggested_new_code)
    """
    issues = []

    if not filepath.exists():
        return issues

    content = filepath.read_text()
    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        # Check for Path("memory/...") patterns
        if "Path(" in line and "memory" in line:
            for old_pattern, new_pattern in PATH_MIGRATIONS.items():
                if old_pattern in line:
                    suggested = line.replace(old_pattern, new_pattern)
                    issues.append((i, line.strip(), suggested.strip()))
                    break

    return issues


def generate_report() -> str:
    """Generate migration report."""
    report = []
    report.append("=" * 70)
    report.append("Path Migration Report - Phase 3")
    report.append("=" * 70)
    report.append("")

    project_root = Path(__file__).parent.parent.parent
    total_issues = 0

    for target_file in TARGET_FILES:
        filepath = project_root / target_file
        issues = analyze_file(filepath)

        if issues:
            total_issues += len(issues)
            report.append(f"\n📄 {target_file}")
            report.append("-" * 70)

            for line_num, old_code, new_code in issues:
                report.append(f"\nLine {line_num}:")
                report.append(f"  OLD: {old_code}")
                report.append(f"  NEW: {new_code}")

    report.append("\n" + "=" * 70)
    report.append(f"Total issues found: {total_issues}")
    report.append("=" * 70)

    return "\n".join(report)


def main():
    """Run path migration audit."""
    print(generate_report())

    print("\n\n💡 Migration Strategy:")
    print("1. Add import: from core.config.paths import get_user_path, get_config_path")
    print("2. Replace Path('memory/...') with get_user_path('...')")
    print("3. Replace string 'memory/...' with str(get_user_path('...'))")
    print("4. Test each file after migration")
    print("\nStart with core services, then handlers, then UI components.")


if __name__ == "__main__":
    main()
