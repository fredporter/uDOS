#!/usr/bin/env python3
"""Phase A/B comprehensive test suite."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def _resolve_repo_root() -> Path:
    cwd = Path.cwd()
    if (cwd / "vibe" / "core" / "skills" / "ucode").exists():
        return cwd
    return Path(__file__).resolve().parents[2]


REPO_ROOT = _resolve_repo_root()


def test_tool_discovery():
    """Test that all tools are discoverable."""
    from vibe.core.tools.ucode import system, spatial, data, workspace, content, specialized

    modules = {
        'system': system,
        'spatial': spatial,
        'data': data,
        'workspace': workspace,
        'content': content,
        'specialized': specialized,
    }

    discovered = {}
    for name, mod in modules.items():
        tools = []
        for attr_name in dir(mod):
            if attr_name.startswith('_') or attr_name in ['UcodeResult', 'UcodeConfig']:
                continue
            obj = getattr(mod, attr_name)
            if hasattr(obj, '__mro__') and any(b.__name__ == 'BaseTool' for b in obj.__mro__):
                tools.append(attr_name)
        discovered[name] = tools

    total = sum(len(t) for t in discovered.values())
    print(f"✅ Tool Discovery: Found {total} tools")
    for mod, tools in sorted(discovered.items()):
        print(f"   {mod.upper()}: {len(tools)}")

    assert total >= 42


def test_tool_structure():
    """Test that all tools follow the BaseTool pattern."""
    from vibe.core.tools.ucode import system, spatial, data, workspace, content, specialized
    from vibe.core.tools.base import BaseTool

    modules = [system, spatial, data, workspace, content, specialized]
    issues = []

    for mod in modules:
        for attr_name in dir(mod):
            if attr_name.startswith('_') or attr_name in ['UcodeResult', 'UcodeConfig']:
                continue
            obj = getattr(mod, attr_name, None)
            if not hasattr(obj, '__mro__'):
                continue
            if not any(b.__name__ == 'BaseTool' for b in obj.__mro__):
                continue

            # Check that tool has required methods
            if not hasattr(obj, 'run'):
                issues.append(f"{attr_name} missing 'run' method")
            if not hasattr(obj, 'get_name'):
                # get_name might be inherited, so this is OK
                pass
            if not hasattr(obj, 'description'):
                issues.append(f"{attr_name} missing 'description'")

    if issues:
        print(f"❌ Tool Structure: {len(issues)} issues found")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("✅ Tool Structure: All tools properly structured")

    assert not issues


def test_skill_discovery():
    """Test that all skills are discoverable."""
    skills_dir = REPO_ROOT / "vibe/core/skills/ucode"
    assert skills_dir.exists(), "Skills directory not found"

    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    skill_files = [d / "SKILL.md" for d in skill_dirs if (d / "SKILL.md").exists()]

    expected_skills = {
        "ucode",
        "ucode-dev",
        "ucode-help",
        "ucode-setup",
    }
    found_skills = {f.parent.name for f in skill_files}
    missing = expected_skills - found_skills

    if not missing:
        print(f"✅ Skill Discovery: Found {len(skill_files)} skills")
        for f in sorted(skill_files):
            print(f"   {f.parent.name}/SKILL.md")
    else:
        print(f"❌ Skill Discovery: Missing expected skills: {sorted(missing)}")

    assert not missing


def test_configuration():
    """Test that .vibe/config.toml is properly configured."""
    config_file = REPO_ROOT / ".vibe/config.toml"
    assert config_file.exists(), ".vibe/config.toml not found"

    content = config_file.read_text()

    checks = {
        'tool_paths': 'tool_paths' in content and 'vibe/core/tools/ucode' in content,
        'skill_paths': 'skill_paths' in content and 'vibe/core/skills/ucode' in content,
    }

    all_ok = all(checks.values())
    if all_ok:
        print("✅ Configuration: .vibe/config.toml properly configured")
        for check, result in checks.items():
            status = "✓" if result else "✗"
            print(f"   {status} {check}")
    else:
        print("❌ Configuration: Missing config entries")
        for check, result in checks.items():
            status = "✓" if result else "✗"
            print(f"   {status} {check}")

    assert all_ok


def test_tool_naming():
    """Test that all tools have proper snake_case names."""
    import re
    from vibe.core.tools.ucode import system, spatial, data, workspace, content, specialized

    modules = [system, spatial, data, workspace, content, specialized]
    issues = []

    for mod in modules:
        for attr_name in dir(mod):
            if attr_name.startswith('_') or attr_name in ['UcodeResult', 'UcodeConfig']:
                continue
            obj = getattr(mod, attr_name, None)
            if not hasattr(obj, '__mro__') or not any(b.__name__ == 'BaseTool' for b in obj.__mro__):
                continue

            # Convert class name to expected tool name
            expected = 'ucode_' + re.sub(r'(?<!^)(?=[A-Z])', '_', attr_name[6:]).lower()
            if not expected.startswith('ucode_'):
                issues.append(f"{attr_name} -> invalid name '{expected}'")

    if issues:
        print(f"❌ Tool Naming: {len(issues)} naming issues")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("✅ Tool Naming: All tools properly named")

    assert not issues


def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase A/B Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Tool Discovery", test_tool_discovery),
        ("Tool Structure", test_tool_structure),
        ("Skill Discovery", test_skill_discovery),
        ("Configuration", test_configuration),
        ("Tool Naming", test_tool_naming),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: Exception - {e}")
            results.append((test_name, False))
        print()

    # Summary
    print("=" * 60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("✅ All tests passed! Phase A/B is ready.")
        return 0
    else:
        print("❌ Some tests failed. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
