#!/bin/bash
# Mock Data Generator
set -euo pipefail

UDEV="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MOCK_DIR="$UDEV/testing/mock-data"

mkdir -p "$MOCK_DIR"

echo "🎭 Generating mock data for testing..."

# Mock user setup data
cat > "$MOCK_DIR/mock-user-setup.json" << 'MOCK'
{
    "username": "devuser",
    "full_name": "Development User", 
    "email": "dev@udos.local",
    "location": "Development City, Dev Country (DV01)",
    "timezone": "UTC",
    "primary_role": "developer",
    "password": "",
    "auto_backup": true,
    "debug_mode": true,
    "preferred_companion": "chester",
    "notification_level": "verbose",
    "experimental_features": true
}
MOCK

# Mock mission data
cat > "$MOCK_DIR/mock-mission-create.json" << 'MOCK'
{
    "mission_name": "Development Test Mission",
    "mission_type": "development",
    "priority_level": "medium",
    "description": "Test mission for development and validation purposes",
    "estimated_duration": "1-2 hours",
    "start_date": "$(date +%Y-%m-%d)",
    "target_completion": "$(date -d '+1 week' +%Y-%m-%d)",
    "required_skills": ["testing", "validation"],
    "resources_needed": ["development_tools"],
    "success_criteria": ["All tests pass", "Validation complete"]
}
MOCK

# Mock system config
cat > "$MOCK_DIR/mock-system-config.json" << 'MOCK'
{
    "display_mode": "console",
    "border_style": "single",
    "color_scheme": "default",
    "logging_level": "DEBUG",
    "enable_debug_mode": true,
    "verbose_output": true,
    "auto_backup_interval": "hourly",
    "backup_retention": "7_days",
    "max_log_size": "10MB",
    "terminal_history_size": "5000",
    "enable_experimental_features": true,
    "network_timeout": "30",
    "command_aliases": true,
    "system_password": ""
}
MOCK

echo "✅ Mock data generated in $MOCK_DIR"
ls -la "$MOCK_DIR"
