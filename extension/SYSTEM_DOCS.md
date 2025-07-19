# 🔌 extension - System Integration Folder

**Purpose**: Official VS Code extension and IDE integration for uDOS v1.0

## 🏗️ System Architecture Role

`extension` is a core system directory that provides professional development environment integration:

### 📁 Directory Structure
```
extension/
├── src/                          # TypeScript extension source code
├── syntaxes/                     # uScript language grammar definitions
├── snippets/                     # uScript code snippet library
├── dist/                         # Compiled extension output (gitignored)
├── out/                          # TypeScript build output (gitignored)
├── package.json                  # Extension manifest and metadata
├── tsconfig.json                 # TypeScript configuration
├── install-extension.sh          # Automated installation script
├── *.vsix                        # Packaged extensions (gitignored)
└── documentation files          # Integration and usage guides
```

### 🔧 System Function

**Local Extension Installation**: Extensions are built and installed locally from this system folder, maintaining uDOS's privacy-first, self-contained architecture.

**Development Integration**: Provides native VS Code support for:
- uScript programming language
- uDOS command execution
- Chester AI companion access
- User role-aware functionality
- System validation and debugging

### 🛡️ Privacy & Security

- **Local Installation**: Extensions install directly from local files, no external dependencies
- **User Role Integration**: Respects uDOS permission matrix (wizard/sorcerer/ghost/imp)
- **Gitignored Artifacts**: Build files and packages excluded from version control
- **System-Level Access**: Integrated with core uDOS command system

### 🚀 Usage

The extension system integrates seamlessly with uDOS workflows:

1. **Automatic Detection**: VS Code tasks detect and use extension
2. **One-Click Install**: `🔌 Install uDOS VS Code Extension` task handles everything
3. **Native Integration**: Extension becomes part of local VS Code environment
4. **System Commands**: Direct access to all uDOS functionality from IDE

---

**The extension completes the uDOS v1.0 professional development environment, providing a fully integrated, privacy-first IDE experience! 🌟**
