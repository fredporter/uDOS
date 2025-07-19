# 🔌 extension - uDOS VS Code Integration Guide

The `extension` folder contains the complete VS Code extension for uDOS v1.0, providing native IDE support for the markdown-native operating system.

## 📦 Installation

### Method 1: Using uDOS Task (Recommended)
1. Open VS Code in your uDOS workspace
2. Run task: `🔌 Install uDOS VS Code Extension`
3. Reload VS Code when prompted

### Method 2: Manual Installation
```bash
cd extension
./install-extension.sh
```

### Method 3: Development Installation
```bash
cd extension
npm install
npm run compile
npm run package
code --install-extension udos-extension-1.0.0.vsix
```

## 🎯 Features Available

### Language Support
- **Syntax Highlighting**: Full uScript (.uscript, .us) syntax highlighting
- **Auto-completion**: IntelliSense for uDOS commands and uScript keywords
- **Snippets**: Pre-built code snippets for common uScript patterns

### Commands Available
Access via Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`):

| Command | Description | Usage |
|---------|-------------|--------|
| `uDOS: Run Command` | Execute any uDOS command | Interactive command execution |
| `uDOS: Validate Installation` | Check system integrity | Verify uDOS setup and permissions |
| `uDOS: Show User Role` | Display current user role | View wizard/sorcerer/ghost/imp status |
| `uDOS: Initialize User` | Set up new user | Configure user profile and permissions |
| `uDOS: Start Chester AI` | Launch Chester companion | Start AI assistant for development help |

### Keyboard Shortcuts
- `Cmd+Shift+U` (Mac) / `Ctrl+Shift+U` (Windows/Linux): Run uDOS Command

### Context Menus
- Right-click `.md` files: "View with Glow" option for enhanced markdown viewing

## 🎮 User Role Integration

The extension automatically adapts to your assigned user role:

### 🧙 wizard
- Full access to all commands and features
- Advanced system administration capabilities
- Chester AI with expert-level assistance

### 🔮 sorcerer  
- Development and scripting focused features
- Code generation and template access
- Chester AI with development assistance

### 👻 ghost
- Read-only exploration and learning mode
- Documentation access and basic commands
- Chester AI with guidance and tutorials

### 😈 imp
- Restricted access with safety controls
- Basic command execution only
- Chester AI with simplified interactions

## 🤖 Chester AI Integration

The extension provides direct integration with Chester, your small dog personality AI companion:

### Chester Commands
- **Error Detection**: Automatic detection of uScript syntax errors
- **Code Suggestions**: Context-aware code completion suggestions  
- **Development Workflow**: Step-by-step guidance through uDOS development
- **Troubleshooting**: Intelligent problem diagnosis and resolution

### Chester Personality Traits
- Small dog enthusiasm and energy
- Expert knowledge of uDOS architecture
- Friendly, helpful guidance style
- Privacy-first recommendations

## 📝 uScript Language Features

### Syntax Highlighting
```uscript
' Comments highlighted in green
SET username AS STRING = "wizard"
IF username = "wizard" THEN
    RUN "CHESTER"
    LOG "Chester activated for wizard user"
END IF
```

### Code Snippets
Type these prefixes and press Tab:
- `mission` → Complete mission template
- `function` → Function definition template
- `if` → If-then-else block
- `for` → For-next loop
- `log` → Logging statement

### Auto-completion
- uDOS commands: `LOG`, `RUN`, `TREE`, `LIST`, `DASH`, etc.
- uScript keywords: `SET`, `IF`, `THEN`, `ELSE`, `FOR`, `FUNCTION`, etc.
- Built-in functions and system calls

## 🔧 Configuration

Extension settings available in VS Code preferences:

### uDOS Settings
- `udos.shellPath`: Path to uDOS shell script (default: `./uCode/ucode.sh`)
- `udos.enableCopilot`: Enable GitHub Copilot integration (default: `true`)

### Workspace Detection
The extension automatically activates when it detects:
- `uCode/ucode.sh` file in workspace
- `.uscript` or `.us` files
- uDOS project structure

## 🚀 Development Workflow

### 1. Write uScript
Create `.uscript` files with full language support:
```uscript
' Example uDOS mission
SET mission_name = "Deploy Application"
LOG "Starting mission: " + mission_name

RUN "VALIDATE SYSTEM"
IF status = "ready" THEN
    RUN "DEPLOY"
    CREATE MILESTONE "Deployment Complete"
END IF
```

### 2. Execute Commands
Use `uDOS: Run Command` to execute any uDOS command directly from VS Code.

### 3. Validate Setup
Regularly run `uDOS: Validate Installation` to ensure system integrity.

### 4. Get Help
Use `uDOS: Start Chester AI` for intelligent assistance and guidance.

## 📚 Next Steps

- Explore the roadmap documents (001-011) for complete uDOS documentation
- Try the pre-configured VS Code tasks (27+ available)
- Experiment with uScript programming using the provided snippets
- Use Chester AI for personalized guidance and development assistance

---

**The uDOS VS Code Extension brings the full power of the markdown-native operating system directly into your development environment! 🌟**
