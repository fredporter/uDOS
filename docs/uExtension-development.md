# uExtension Development Documentation

## 🔧 Security Level 2: Local Development Only

The `uExtension/` directory contains VS Code extension source code and is **NEVER included in the repository**. Extensions are distributed through uKnowledge packages or VS Code marketplace.

### Directory Structure (Local Development)

```
uExtension/
├── package.json        # Extension metadata and dependencies
├── tsconfig.json       # TypeScript configuration
├── src/
│   ├── extension.ts    # Main extension entry point
│   ├── commands/       # uDOS command implementations
│   ├── language/       # uScript language support
│   └── providers/      # VS Code providers (completion, etc.)
├── syntaxes/           # uScript syntax highlighting
├── snippets/           # Code snippets for uDOS/uScript
├── themes/             # uDOS color themes
├── icons/              # Extension icons and assets
├── out/                # Compiled JavaScript (gitignored)
├── node_modules/       # Dependencies (gitignored)
└── *.vsix              # Packaged extension (gitignored)
```

### Distribution Strategy

Instead of including source in repository, extensions are distributed via:

1. **uKnowledge Packages**: Install scripts in `uKnowledge/packages/`
2. **VS Code Marketplace**: Published extension (future)
3. **Release Artifacts**: Pre-built `.vsix` files in GitHub releases
4. **Local Building**: Users can build from documented structure

### Installation Process

```bash
# During uDOS installation
./install-udos.sh
# Automatically sets up uExtension/ locally
# Installs pre-built extension or builds from template

# Manual extension development
./uCode/setup-extension-dev.sh
# Creates local uExtension/ with full source
# Sets up development environment
```

### Security Benefits

- ✅ Source code not exposed in public repository
- ✅ Reduces repository size and complexity
- ✅ Allows for rapid extension development cycles
- ✅ Maintains clean separation between core system and tools
- ✅ Enables private/custom extension development

### Development Workflow

1. **Install uDOS**: Core system without extension source
2. **Setup Development**: Run setup script to create uExtension/
3. **Develop**: Edit, test, debug extension locally
4. **Package**: Build `.vsix` for distribution
5. **Distribute**: Via uKnowledge packages or marketplace

### Extension Features

The uDOS VS Code extension provides:

- ✅ uScript language support (syntax highlighting, IntelliSense)
- ✅ uDOS command palette integration
- ✅ Template insertion and generation
- ✅ User role awareness and permission enforcement
- ✅ Chester AI companion integration
- ✅ Markdown-native file operations
- ✅ Project structure navigation
- ✅ Integrated terminal with uDOS commands

---

*Extension source is created locally during development setup and maintained separately from the core uDOS repository.*
