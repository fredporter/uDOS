#!/bin/bash
# Mock Data Generator for Testing
UDEV="$(dirname "$0")"
mkdir -p "$UDEV/testing/mock-data"

echo "Generating mock dataget data..."
cat > "$UDEV/testing/mock-data/test-user-setup.json" << 'MOCK'
{
    "username": "testuser123",
    "full_name": "Test User",
    "email": "test@example.com",
    "location": "Test City, Test Country (TX01)",
    "timezone": "UTC",
    "primary_role": "developer",
    "password": "",
    "auto_backup": true,
    "debug_mode": false,
    "preferred_companion": "chester",
    "notification_level": "standard",
    "experimental_features": false
}
MOCK

echo "✅ Mock data generated in $UDEV/testing/mock-data/"
