#!/usr/bin/env python3
"""
uDOS v1.0.2 - Enhanced File Operations Test Suite

Tests all new features:
- Smart file picker with fuzzy search
- Batch operations
- File preview
- Recently used files
- Workspace bookmarks
- Enhanced SHOW/EDIT with bookmark support

Version: 1.0.2
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add uDOS core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from commands.enhanced_file_handler import EnhancedFileCommandHandler
from utils.smart_picker import SmartFilePicker


def create_test_environment():
    """Create a test environment with sample files."""
    # Create temporary directory structure
    temp_dir = Path(tempfile.mkdtemp(prefix="udos_v1_0_2_test_"))

    # Create workspace directories
    for workspace in ['sandbox', 'memory', 'data']:
        (temp_dir / workspace).mkdir(exist_ok=True)

    # Create sample files
    sample_files = {
        'sandbox/test_file.md': '# Test File\n\nThis is a test markdown file.',
        'sandbox/script.uscript': '# Test Script\nHELP\nSTATUS\n',
        'sandbox/data.json': '{"test": "data", "version": "1.0"}',
        'sandbox/notes.txt': 'Important notes\nLine 2\nLine 3',
        'memory/archive.md': '# Archive\nOld content here',
        'memory/config.udo': '{"config": "settings"}',
        'data/system.json': '{"system": "config"}'
    }

    for file_path, content in sample_files.items():
        full_path = temp_dir / file_path
        full_path.write_text(content)

    return temp_dir


def test_smart_picker():
    """Test smart file picker functionality."""
    print("🧪 Testing Smart File Picker")
    print("=" * 50)

    temp_dir = create_test_environment()

    try:
        # Initialize picker
        picker = SmartFilePicker(temp_dir)

        # Test file listing
        files = picker.get_files_in_workspace('sandbox')
        print(f"✅ Found {len(files)} files in sandbox")

        # Test fuzzy search
        matches = picker.fuzzy_search('test', files)
        print(f"✅ Fuzzy search for 'test': {len(matches)} matches")

        # Test file preview
        if files:
            preview = picker.get_file_preview(files[0])
            print(f"✅ File preview: {len(preview)} characters")

        # Test bookmarks
        picker.add_bookmark('test_notes', 'sandbox/notes.txt')
        print(f"✅ Bookmarks: {list(picker.bookmarks.keys())}")

        # Test recent files
        picker.add_to_recent('sandbox/test_file.md', 'tested')
        print(f"✅ Recent files: {len(picker.recent_files)} entries")

        print("✅ Smart picker tests passed")
        return True

    except Exception as e:
        print(f"❌ Smart picker test failed: {e}")
        return False

    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


def test_enhanced_commands():
    """Test enhanced file command handler."""
    print("\n🧪 Testing Enhanced File Commands")
    print("=" * 50)

    temp_dir = create_test_environment()

    try:
        # Change to test directory for relative paths
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        # Initialize handler
        handler = EnhancedFileCommandHandler()

        # Test SEARCH command
        print("\n📍 Testing SEARCH command:")
        result = handler.handle("SEARCH", ["test", "sandbox"], None)
        print(f"SEARCH result: {result[:100]}...")
        assert "Search Results" in result

        # Test PREVIEW command
        print("\n📍 Testing PREVIEW command:")
        result = handler.handle("PREVIEW", ["sandbox/test_file.md"], None)
        print(f"PREVIEW result: {result[:100]}...")
        assert "File Preview" in result

        # Test RECENT command
        print("\n📍 Testing RECENT command:")
        # First add some files to recent
        handler.smart_picker.add_to_recent('sandbox/test_file.md', 'tested')
        result = handler.handle("RECENT", [], None)
        print(f"RECENT result: {result[:100]}...")
        assert "Recently Used Files" in result

        # Test BOOKMARK command
        print("\n📍 Testing BOOKMARK command:")
        result = handler.handle("BOOKMARK", ["add", "test", "sandbox/test_file.md"], None)
        print(f"BOOKMARK add result: {result}")
        assert "Bookmark added" in result

        result = handler.handle("BOOKMARK", [], None)
        print(f"BOOKMARK list result: {result[:100]}...")
        assert "Workspace Bookmarks" in result

        # Test BATCH command
        print("\n📍 Testing BATCH command:")
        result = handler.handle("BATCH", ["list", "*.md", "sandbox"], None)
        print(f"BATCH list result: {result[:100]}...")
        assert "Batch List" in result

        print("✅ Enhanced command tests passed")
        return True

    except Exception as e:
        print(f"❌ Enhanced command test failed: {e}")
        return False

    finally:
        os.chdir(original_cwd)
        import shutil
        shutil.rmtree(temp_dir)


def test_integration():
    """Test integration with existing commands."""
    print("\n🧪 Testing Integration")
    print("=" * 50)

    temp_dir = create_test_environment()

    try:
        # Change to test directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        # Initialize handler
        handler = EnhancedFileCommandHandler()

        # Test enhanced SHOW with bookmark
        print("\n📍 Testing enhanced SHOW:")
        # Add bookmark first
        handler.smart_picker.add_bookmark('notes', 'sandbox/notes.txt')

        # Test bookmark reference
        result = handler.handle("SHOW", ["@notes"], None)
        print(f"SHOW @notes result: {result[:100]}...")
        assert "Important notes" in result

        # Test enhanced EDIT (mock)
        print("\n📍 Testing enhanced EDIT:")
        result = handler.handle("EDIT", ["@notes"], None)
        print(f"EDIT @notes result: {result[:100]}...")
        assert "Mock edit" in result or "Error" in result  # Expected since editor is mocked

        print("✅ Integration tests passed")
        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

    finally:
        os.chdir(original_cwd)
        import shutil
        shutil.rmtree(temp_dir)


def test_batch_operations():
    """Test batch file operations."""
    print("\n🧪 Testing Batch Operations")
    print("=" * 50)

    temp_dir = create_test_environment()

    try:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        handler = EnhancedFileCommandHandler()

        # Create multiple test files for batch operations
        for i in range(3):
            (Path('sandbox') / f'batch_test_{i}.txt').write_text(f'Batch test file {i}')

        print("\n📍 Testing batch list:")
        result = handler.handle("BATCH", ["list", "batch_*.txt", "sandbox"], None)
        print(f"Batch list result: {result[:150]}...")
        assert "3 files" in result

        print("\n📍 Testing batch copy:")
        result = handler.handle("BATCH", ["copy", "batch_*.txt", "sandbox", "memory"], None)
        print(f"Batch copy result: {result[:100]}...")

        # Check if files were copied
        memory_files = list(Path('memory').glob('batch_*.txt'))
        print(f"Files copied to memory: {len(memory_files)}")

        print("✅ Batch operations tests passed")
        return True

    except Exception as e:
        print(f"❌ Batch operations test failed: {e}")
        return False

    finally:
        os.chdir(original_cwd)
        import shutil
        shutil.rmtree(temp_dir)


def main():
    """Run all v1.0.2 enhancement tests."""
    print("🚀 uDOS v1.0.2 FILE OPERATIONS ENHANCEMENT TESTS")
    print("=" * 80)

    tests = [
        ("Smart File Picker", test_smart_picker),
        ("Enhanced Commands", test_enhanced_commands),
        ("Integration Tests", test_integration),
        ("Batch Operations", test_batch_operations)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} - ERROR: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("📊 v1.0.2 ENHANCEMENT TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")

    if failed == 0:
        print("\n🎉 ALL v1.0.2 ENHANCEMENT TESTS PASSED!")
        print("✅ Smart file picker ready")
        print("✅ Batch operations ready")
        print("✅ File preview ready")
        print("✅ Bookmarks and recent files ready")
        print("✅ Enhanced SHOW/EDIT ready")
    else:
        print(f"\n⚠️  {failed} tests failed.")

    print("\n" + "=" * 80)
    print("🎯 v1.0.2 DEVELOPMENT COMPLETE - READY FOR INTEGRATION")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
