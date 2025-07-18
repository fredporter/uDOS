# uExtension - uDOS VS Code Integration v1.0

**Official VS Code extension for uDOS v1.0 - the markdown-native operating system**

The `uExtension` folder is a core system directory containing the VS Code extension that provides native IDE support for uDOS development and operation.

## 🏗️ System Architecture Role

`uExtension` serves as the official IDE integration layer for uDOS:
- **Language Support**: Complete uScript programming language integration
- **Command Interface**: Direct access to all uDOS commands from VS Code
- **Development Tools**: Professional tooling for uDOS system development
- **Local Installation**: Extensions install locally to VS Code from this system folder

## 🚀 Features

- **uScript Language Support**: Complete syntax highlighting for uScript (.uscript, .us files)
- **Command Integration**: Direct access to uDOS commands from VS Code
- **User Role Awareness**: Integration with uDOS user role system (wizard/sorcerer/ghost/imp)
- **Chester AI Integration**: Direct access to Chester companion commands
- **Installation Validation**: Built-in system health and integrity checking
- **Auto-completion**: IntelliSense for uScript keywords and uDOS commands

## 📦 Installation

1. **From VS Code Marketplace** (when published):
   - Search for "uDOS" in VS Code Extensions
   - Install "uDOS v1.0 - User DOS Shell"

2. **Manual Installation** (development):
   ```bash
   cd uDOS-Extension
   npm install
   npm run compile
   # Install via VS Code: "Extensions: Install from VSIX"
   ```

## 🎯 Commands Available

- `uDOS: Run Command` - Execute any uDOS command
- `uDOS: Validate Installation` - Check system integrity
- `uDOS: Show User Role` - Display current user role
- `uDOS: Initialize User` - Set up new user configuration
- `uDOS: Start Chester` - Launch Chester AI companion

## 🛠️ Requirements

- VS Code 1.60.0 or higher
- uDOS v1.0 installation
- Valid user role assignment

## 📝 uScript Language Support

The extension provides full language support for uScript files:

```uscript
' Example uScript with syntax highlighting
SET username AS STRING = "wizard"
IF username = "wizard" THEN
    RUN "CHESTER"
    LOG "Chester activated for wizard user"
END IF
```

## 🎮 User Role Integration

Commands and features automatically adapt to your assigned user role:
- **wizard**: Full system access and advanced commands
- **sorcerer**: Development and scripting capabilities  
- **ghost**: Read-only system exploration
- **imp**: Restricted access with basic commands

## 🤖 Chester Integration

Direct integration with Chester AI companion:
- Contextual help and guidance
- Error detection and resolution
- Development workflow assistance
- Small dog personality traits in all interactions

## 📚 Documentation

For complete uDOS documentation, see the main repository roadmap documents (001-011).

## 🔧 Development

Built with TypeScript and the VS Code Extension API:
- `src/extension.ts` - Main extension logic
- `package.json` - Extension manifest and configuration
- `syntaxes/` - uScript language grammar
- `snippets/` - uScript code snippets

---

**Part of uDOS v1.0 - The complete markdown-native operating system**
