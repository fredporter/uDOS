#!/usr/bin/env python3
"""
Create initial dev.json configuration (local-only, gitignored)
"""

import json
from pathlib import Path

config = {
    "host": "127.0.0.1",
    "port": 8766,
    "debug": True,
    "services": {
        "runtime_execution_enabled": True,
        "task_scheduler_enabled": True,
        "project_management": True,
    },
    "ai_routing": {
        "local_model": "ollama",
        "remote_provider": "openrouter",
        "max_daily_calls": 50,
    },
}

config_path = Path(__file__).parent / "dev.json"
config_path.write_text(json.dumps(config, indent=2))
print(f"Created {config_path}")
