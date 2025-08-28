# Development Examples for AI Assistants

## Common Development Tasks

### Creating New Extensions
```bash
# Work in dev/active/extensions/
cd dev/active/extensions/
mkdir my-new-extension/
# Use templates from dev/templates/extensions/
```

### Core System Development
```bash
# Work in dev/active/core/
cd dev/active/core/
# Use build scripts from dev/scripts/build/
```

### Testing and Validation
```bash
# Use test scripts from dev/scripts/test/
./dev/scripts/test/validate-system-references.sh
./dev/scripts/test/test-integration-compatibility.sh
```

## File Patterns
- Core development → `/dev/active/`
- User experiments → `/sandbox/experiments/`
- Temporary scripts → `/sandbox/scripts/`
- Permanent tools → `/dev/tools/`

## Git Sync Patterns
- Sync: `/dev/templates/`, `/dev/docs/`, roadmaps
- Local only: `/dev/active/`, temporary work
- User only: `/sandbox/` (flushable)
