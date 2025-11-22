from pathlib import Path
import json
from typing import Dict, Any


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def load_theme(theme_name: str = 'dungeon', root_path: Path = None) -> Dict[str, Dict[str, Any]]:
    """
    Load a theme lexicon by merging the bundled theme under `knowledge` with
    optional user overrides in `memory`.

    Precedence: memory override (if present) > knowledge bundled theme.

    Returns a dict with keys: 'TERMINOLOGY', 'MESSAGES', 'META', and optionally
    'THEME_NAME', 'VERSION', 'NAME', 'STYLE', 'DESCRIPTION', 'ICON'.
    """
    if root_path is None:
        root_path = Path(__file__).parent.parent.parent

    knowledge_theme_path = root_path / 'knowledge' / 'system' / 'themes' / f"{theme_name}.json"
    memory_theme_path = root_path / 'memory' / 'system' / 'themes' / f"{theme_name}.json"

    # Merge themes (memory overrides knowledge)
    merged = {
        'TERMINOLOGY': {},
        'MESSAGES': {},
        'META': {
            'theme_name': theme_name,
            'source_knowledge': str(knowledge_theme_path) if knowledge_theme_path.exists() else None,
            'source_memory': str(memory_theme_path) if memory_theme_path.exists() else None
        }
    }

    # Load from bundled knowledge first
    if knowledge_theme_path.exists():
        with knowledge_theme_path.open('r', encoding='utf-8') as f:
            knowledge_data = json.load(f)
            merged['TERMINOLOGY'].update(knowledge_data.get('TERMINOLOGY', {}))
            merged['MESSAGES'].update(knowledge_data.get('MESSAGES', {}))
            # Copy metadata fields
            for key in ['THEME_NAME', 'VERSION', 'NAME', 'STYLE', 'DESCRIPTION', 'ICON']:
                if key in knowledge_data:
                    merged[key] = knowledge_data[key]

    # Overlay user customizations from memory
    if memory_theme_path.exists():
        with memory_theme_path.open('r', encoding='utf-8') as f:
            memory_data = json.load(f)
            merged['TERMINOLOGY'].update(memory_data.get('TERMINOLOGY', {}))
            merged['MESSAGES'].update(memory_data.get('MESSAGES', {}))
            # User can override metadata too
            for key in ['THEME_NAME', 'VERSION', 'NAME', 'STYLE', 'DESCRIPTION', 'ICON']:
                if key in memory_data:
                    merged[key] = memory_data[key]

    return merged
