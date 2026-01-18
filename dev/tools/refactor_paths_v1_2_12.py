#!/usr/bin/env python3
"""
Bulk Path Refactoring Script for v1.2.12
Replaces hardcoded paths with PATHS constants across codebase
"""

import re
from pathlib import Path
from typing import List, Tuple

# Path mappings (hardcoded -> PATHS constant)
PATH_REPLACEMENTS = {
    # Workflow paths
    r'Path\("memory/workflows/missions"\)': 'PATHS.MEMORY_WORKFLOWS_MISSIONS',
    r'"memory/workflows/missions"': 'str(PATHS.MEMORY_WORKFLOWS_MISSIONS)',
    r"'memory/workflows/missions'": 'str(PATHS.MEMORY_WORKFLOWS_MISSIONS)',
    
    r'Path\("memory/workflows/checkpoints"\)': 'PATHS.MEMORY_WORKFLOWS_CHECKPOINTS',
    r'"memory/workflows/checkpoints"': 'str(PATHS.MEMORY_WORKFLOWS_CHECKPOINTS)',
    r"'memory/workflows/checkpoints'": 'str(PATHS.MEMORY_WORKFLOWS_CHECKPOINTS)',
    
    r'Path\("memory/workflows/state"\)': 'PATHS.MEMORY_WORKFLOWS_STATE',
    r'"memory/workflows/state"': 'str(PATHS.MEMORY_WORKFLOWS_STATE)',
    r"'memory/workflows/state'": 'str(PATHS.MEMORY_WORKFLOWS_STATE)',
    
    r'Path\("memory/workflows/state/current\.json"\)': 'PATHS.WORKFLOW_STATE',
    r'"memory/workflows/state/current\.json"': 'str(PATHS.WORKFLOW_STATE)',
    r"'memory/workflows/state/current\.json'": 'str(PATHS.WORKFLOW_STATE)',
    
    # System paths
    r'Path\("memory/system/user/checklist_state\.json"\)': 'PATHS.CHECKLIST_STATE',
    r'"memory/system/user/checklist_state\.json"': 'str(PATHS.CHECKLIST_STATE)',
    r"'memory/system/user/checklist_state\.json'": 'str(PATHS.CHECKLIST_STATE)',
    
    r'Path\("memory/system/webhooks\.json"\)': 'PATHS.WEBHOOKS_CONFIG',
    r'"memory/system/webhooks\.json"': 'str(PATHS.WEBHOOKS_CONFIG)',
    r"'memory/system/webhooks\.json'": 'str(PATHS.WEBHOOKS_CONFIG)',
    
    # Draft paths
    r'Path\("memory/drafts/svg"\)': 'PATHS.MEMORY_DRAFTS_SVG',
    r'"memory/drafts/svg"': 'str(PATHS.MEMORY_DRAFTS_SVG)',
    r"'memory/drafts/svg'": 'str(PATHS.MEMORY_DRAFTS_SVG)',
    
    r'Path\("memory/drafts/ascii"\)': 'PATHS.MEMORY_DRAFTS_ASCII',
    r'"memory/drafts/ascii"': 'str(PATHS.MEMORY_DRAFTS_ASCII)',
    r"'memory/drafts/ascii'": 'str(PATHS.MEMORY_DRAFTS_ASCII)',
    
    r'Path\("memory/drafts/teletext"\)': 'PATHS.MEMORY_DRAFTS_TELETEXT',
    r'"memory/drafts/teletext"': 'str(PATHS.MEMORY_DRAFTS_TELETEXT)',
    r"'memory/drafts/teletext'": 'str(PATHS.MEMORY_DRAFTS_TELETEXT)',
    
    # Log paths
    r'Path\("memory/logs"\)': 'PATHS.MEMORY_LOGS',
    r'"memory/logs"': 'str(PATHS.MEMORY_LOGS)',
    r"'memory/logs'": 'str(PATHS.MEMORY_LOGS)',
    
    # UCode paths
    r'Path\("memory/ucode/adventures"\)': 'PATHS.MEMORY_UCODE_ADVENTURES',
    r'"memory/ucode/adventures"': 'str(PATHS.MEMORY_UCODE_ADVENTURES)',
    r"'memory/ucode/adventures'": 'str(PATHS.MEMORY_UCODE_ADVENTURES)',
    
    # Deprecated sandbox paths
    r'Path\("sandbox/user"\)': 'PATHS.MEMORY_SYSTEM_USER',
    r'"sandbox/user"': 'str(PATHS.MEMORY_SYSTEM_USER)',
    r"'sandbox/user'": 'str(PATHS.MEMORY_SYSTEM_USER)',
}

IMPORT_STATEMENT = "from core.utils.paths import PATHS"


def has_paths_import(content: str) -> bool:
    """Check if file already imports PATHS"""
    return "from core.utils.paths import PATHS" in content


def add_paths_import(content: str) -> str:
    """Add PATHS import after other imports"""
    lines = content.split('\n')
    
    # Find last import line
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith(('import ', 'from ')):
            last_import_idx = i
    
    # Insert PATHS import
    lines.insert(last_import_idx + 1, IMPORT_STATEMENT)
    return '\n'.join(lines)


def refactor_file(file_path: Path) -> Tuple[bool, int]:
    """Refactor a single file. Returns (changed, replacement_count)"""
    try:
        content = file_path.read_text()
        original = content
        replacements = 0
        
        # Apply path replacements
        for pattern, replacement in PATH_REPLACEMENTS.items():
            new_content, count = re.subn(pattern, replacement, content)
            if count > 0:
                content = new_content
                replacements += count
        
        # Add import if replacements were made and import doesn't exist
        if replacements > 0 and not has_paths_import(content):
            content = add_paths_import(content)
        
        # Write back if changed
        if content != original:
            file_path.write_text(content)
            return True, replacements
        
        return False, 0
    
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, 0


def main():
    """Refactor all Python files in core/commands and core/services"""
    root = Path(".")
    
    # Target directories
    targets = [
        root / "core" / "commands",
        root / "core" / "services",
        root / "extensions" / "play" / "commands",
        root / "extensions" / "play" / "services",
    ]
    
    total_files = 0
    total_changed = 0
    total_replacements = 0
    
    print("🔧 v1.2.12 Path Refactoring Script")
    print("=" * 60)
    
    for target_dir in targets:
        if not target_dir.exists():
            continue
        
        print(f"\n📁 Processing {target_dir}/...")
        
        for py_file in target_dir.rglob("*.py"):
            # Skip __pycache__ and .archive
            if '__pycache__' in str(py_file) or '.archive' in str(py_file):
                continue
            
            total_files += 1
            changed, replacements = refactor_file(py_file)
            
            if changed:
                total_changed += 1
                total_replacements += replacements
                print(f"  ✅ {py_file.name}: {replacements} replacements")
    
    print("\n" + "=" * 60)
    print(f"📊 Summary:")
    print(f"  Files processed: {total_files}")
    print(f"  Files changed: {total_changed}")
    print(f"  Total replacements: {total_replacements}")
    print(f"\n✅ Refactoring complete!")


if __name__ == "__main__":
    main()
