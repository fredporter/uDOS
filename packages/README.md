# uDOS Packages

Distribution packages for uDOS Alpha.

## Package Types

| Type | Format | Target | Description |
|------|--------|--------|-------------|
| **TCZ** | `.tcz` | Tiny Core Linux | Squashfs packages for TinyCore |
| **Extension** | `.udos-ext` | All platforms | Python/JS extensions |
| **Plugin** | `.udos-plugin` | uCode Markdown App | Svelte components |

## Directory Structure

```
packages/
├── .templates/           # Package templates
│   ├── tcz/
│   ├── extension/
│   └── plugin/
├── core/                 # Core system packages
├── knowledge/            # Knowledge bank packages
├── wizard/               # Wizard-only packages
└── contrib/              # Community contributions
```

## Package Manifest

Every package requires a `manifest.json`:

```json
{
  "name": "package-name",
  "version": "1.0.0",
  "type": "tcz|extension|plugin",
  "description": "What this package does",
  "author": "Author Name",
  "license": "MIT",
  "dependencies": [],
  "platform": ["tinycore", "macos", "linux", "windows"],
  "min_udos_version": "1.0.0.0"
}
```

## Building Packages

```bash
# Build TCZ package
python -m core.commands.build_handler tcz core

# Build extension
python -m packages.build extension my-extension

# Build plugin
python -m packages.build plugin my-plugin
```

## Distribution

**Alpha Distribution:**
- Local file system (`/packages/`)
- Git repository releases
- Manual TCZ installation

**Future (v1.1+):**
- Plugin repository server
- Automatic updates
- Signed packages

---

*Last Updated: 2026-01-05*
*Version: Alpha v1.0.0.28*
