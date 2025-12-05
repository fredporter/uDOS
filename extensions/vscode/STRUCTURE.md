# VS Code Extension - File Structure

## Active Files

### Documentation
- `README.md` - Main extension documentation (features, setup, usage)
- `TESTING-GUIDE.md` - Testing procedures and quality checks
- `TROUBLESHOOTING.md` - Common issues and solutions

### Setup
- `enable-extension.sh` - Development setup script (symlink-based)
- `package.json` - Extension manifest and dependencies
- `tsconfig.json` - TypeScript configuration

### Source Code (`src/`)
- `extension.ts` - Main extension entry point
- `providers/completion.ts` - IntelliSense provider
- `providers/hover.ts` - Hover documentation provider
- `commands/executor.ts` - Script execution
- `commands/knowledge-checker.ts` - Knowledge quality validation
- `commands/image-validator.ts` - Image content validation

### Language Support
- `snippets/upy.json` - Code snippets (master copy)
- `syntaxes/upy.tmLanguage.json` - TextMate grammar
- `language-configuration.json` - Language rules (brackets, comments)

### Assets
- `images/` - Extension icons and branding

### Test Files (`test-examples/`)
- `feature-test.upy` - Feature demonstration script
- `knowledge-workflow.upy` - Knowledge guide workflow
- `water-filter-mission.upy` - Complete mission example

## Build Output (Not Committed)
- `out/` - Compiled JavaScript (.gitignore)
- `node_modules/` - Dependencies (.gitignore)
- `.archive/` - Deprecated files (.gitignore)

## Archived Files (Local Only, Not in Git)

The following files were archived to `.archive/` on Dec 5, 2025:

### Documentation (Redundant)
- `.archive/docs/DEMO.md` - Feature demos (now in README.md)
- `.archive/docs/EXTENSION-SETUP.md` - Setup guide (consolidated)
- `.archive/docs/QUICK-START.md` - Quick start (in README.md)
- `.archive/docs/QUICK-START-WORKSPACE.md` - Workspace setup (in README.md)
- `.archive/docs/WORKSPACE-INTEGRATION.md` - Integration guide (in README.md)

### Scripts (Deprecated)
- `.archive/setup.sh` - Old npm-based setup (replaced by enable-extension.sh)

**Reason for archiving**: Multiple overlapping guides caused confusion. README.md now serves as the single source of truth.

## File Count
- **3** markdown docs (active)
- **1** setup script
- **7** source files
- **3** config files
- **3** test examples
- **Total**: ~17 essential files (excluding build outputs)

## Development Workflow

1. **Edit** source in `src/`
2. **Build** with `npm run compile` (or F5 in VS Code)
3. **Test** with "Run VS Code Extension" launch config
4. **Enable** with `./enable-extension.sh` for workspace use

## Version Control

- ✅ Committed: Source code, docs, configs, test files
- ❌ Ignored: Build outputs, dependencies, archives
