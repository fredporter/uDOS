# Getting Started with VS Code for uDOS Dev Mode

## 🚀 **Development Environment Setup Guide**

**Target Audience**: Wizard Installation users with Dev Mode access  
**Prerequisites**: VS Code installed, uDOS wizard directory access  
**Scope**: Complete VS Code setup and workflow for uDOS development

---

## 📋 **Quick Start Checklist**

- [ ] VS Code installed on your system
- [ ] Wizard Installation with Dev Mode enabled
- [ ] Access to `/Users/agentdigital/uDOS/wizard/` directory
- [ ] Basic familiarity with VS Code interface
- [ ] Git configured for version control

---

## 🎯 **1. Opening the uDOS Development Workspace**

### **Method A: From Terminal (Recommended)**
```bash
# Navigate to uDOS wizard directory
cd /Users/agentdigital/uDOS/wizard

# Launch VS Code with the uDOS workspace
code vscode/
```

### **Method B: From VS Code**
1. Open VS Code
2. **File** → **Open Workspace from File...**
3. Navigate to `/Users/agentdigital/uDOS/wizard/vscode/`
4. Select the workspace configuration file

### **Method C: From Finder (macOS)**
1. Navigate to `/Users/agentdigital/uDOS/wizard/vscode/`
2. Right-click on the directory
3. **Open with** → **Visual Studio Code**

---

## 🏗️ **2. Understanding the Dev Mode Environment**

### **Workspace Structure Overview**
```
wizard/
├── vscode/                    # 🎯 VS Code configuration hub
│   ├── .vscode/              # Workspace settings and tasks
│   │   ├── settings.json     # uDOS-specific editor settings
│   │   ├── tasks.json        # Build, run, and test tasks
│   │   ├── launch.json       # Debug configurations
│   │   └── snippets/         # uCode and uDOS code snippets
│   └── vscode-extension/     # uDOS VS Code Extension
│       ├── package.json      # Extension configuration
│       ├── snippets/         # Code completion snippets
│       └── syntaxes/         # uCode syntax highlighting
├── notes/                    # 📚 Historical documentation
├── workflows/                # 🔄 Workflow management
│   └── workflows/           # Wizard workflow management (Level 100)
└── utilities/               # 🛠️ Development tools and scripts
```

### **Key Directories for Development**
- **`vscode/`** - Your VS Code workspace and configuration
- **`notes/`** - Historical documentation and implementation records
- **`wizard/workflows/roadmaps/`** - Strategic planning and future development (uTASK-* files)
- **`utilities/`** - Development tools and helper scripts

---

## 🔧 **3. Essential VS Code Extensions for uDOS Development**

### **Core Extensions (Install First)**
```bash
# Markdown development (essential for uDOS documentation)
code --install-extension yzhang.markdown-all-in-one

# Spell checking for documentation quality
code --install-extension streetsidesoftware.code-spell-checker

# Enhanced Git integration
code --install-extension eamodio.gitlens

# Shell script support for uDOS scripts
code --install-extension timonwong.shellcheck
```

### **Productivity Extensions (Recommended)**
```bash
# File management and navigation
code --install-extension alefragnani.project-manager

# Terminal enhancements
code --install-extension ms-vscode.terminal

# JSON editing for uDOS configuration files
code --install-extension ms-vscode.json

# ASCII art and drawing tools
code --install-extension cweijan.vscode-ascii-art
```

### **Development Extensions (Advanced)**
```bash
# Docker support (for future containerization)
code --install-extension ms-azuretools.vscode-docker

# REST client for API testing
code --install-extension humao.rest-client

# Code formatting and linting
code --install-extension esbenp.prettier-vscode
```

---

## 🎨 **4. uCode Script Development Workflow**

### **Creating a New uCode Script**

#### **Step 1: Navigate to uSCRIPT Library**
1. **File** → **Open Folder**
2. Navigate to `/Users/agentdigital/uDOS/uSCRIPT/library/ucode/`
3. Or use Ctrl+K, Ctrl+O (quick folder open)

#### **Step 2: Create New Script File**
1. Right-click in Explorer panel
2. **New File** → `YourScript.ucode`
3. Or use Ctrl+N for new file, then Ctrl+S to save

#### **Step 3: Use uCode Template Snippets**
1. In your new `.ucode` file, type: `ucode-template`
2. Press **Tab** to expand the full script template
3. Fill in the placeholders with your specific functionality

### **Available Code Snippets**
Type these and press Tab for instant code generation:

- `ucode-template` - Complete script structure with headers
- `ucode-function` - Function declaration with parameters
- `ucode-if` - IF/THEN/ELSE statement block
- `ucode-select` - SELECT CASE statement
- `ucode-for` - FOR loop with iterator
- `ucode-panel` - ASCII panel rendering code
- `ucode-config` - Configuration loading pattern

---

## 🧪 **5. Testing and Running uCode Scripts**

### **Using Integrated Terminal**
1. **Open Terminal**: Ctrl+` (backtick) or **Terminal** → **New Terminal**
2. **Navigate to uDOS root**:
   ```bash
   cd /Users/agentdigital/uDOS
   ```

### **Testing Script Syntax**
```bash
# Validate script syntax before running
./uCORE/code/ucode-modular.sh TEST_SCRIPT YourScript

# Check for common issues
./uCORE/code/ucode-modular.sh VALIDATE_SCRIPT YourScript
```

### **Running Scripts**
```bash
# Execute script with arguments
./uCORE/code/ucode-modular.sh RUN_SCRIPT YourScript arg1 arg2

# Run in debug mode for troubleshooting
./uCORE/code/ucode-modular.sh DEBUG_SCRIPT YourScript
```

### **Using VS Code Tasks**
1. **Terminal** → **Run Task** (Ctrl+Shift+P → "Tasks: Run Task")
2. Select from pre-configured tasks:
   - **Build uCode Script** - Syntax validation
   - **Run uCode Script** - Execute with arguments
   - **Test uCode Script** - Run with test data
   - **Deploy Script** - Move to production library

---

## 🐛 **6. Debugging uCode Scripts**

### **Debug Configuration Setup**
VS Code includes pre-configured debug settings in `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug uCode Script",
            "type": "node",
            "request": "launch",
            "program": "${workspaceFolder}/uCORE/code/ucode-modular.sh",
            "args": ["DEBUG_SCRIPT", "${fileBasenameNoExtension}"],
            "console": "integratedTerminal"
        }
    ]
}
```

### **Debugging Workflow**
1. **Set Breakpoints**: Click in the gutter next to line numbers
2. **Start Debugging**: F5 or **Run** → **Start Debugging**
3. **Debug Console**: View variables and execute commands
4. **Step Through Code**: F10 (step over), F11 (step into)

### **Debug Output in Scripts**
```vb
' Add comprehensive debug output
IF debug_mode THEN
    PRINT "🐛 DEBUG: Processing file: " + filename
    PRINT "🐛 DEBUG: Current directory: " + current_dir
    LOG_MESSAGE("DEBUG", "Function: " + FUNCTION_NAME + " - Variable state: " + STR(counter))
END IF
```

---

## 🎯 **7. Advanced Development Features**

### **IntelliSense for uCode**
- **Auto-completion** for uCode keywords (DIM, FUNCTION, IF, etc.)
- **Function signatures** with parameter hints
- **Hover documentation** for built-in functions
- **Error highlighting** for syntax issues
- **Go to definition** for custom functions

### **File Navigation Power Features**
- **Quick Open**: Ctrl+P to instantly open any file
- **Go to Symbol**: Ctrl+Shift+O for functions in current file
- **Go to Definition**: F12 on function names
- **Find in Files**: Ctrl+Shift+F across entire project
- **Breadcrumb Navigation**: Click path elements at top

### **Multi-cursor Editing**
- **Add Cursor**: Alt+Click anywhere
- **Select All Occurrences**: Ctrl+Shift+L
- **Select Next Occurrence**: Ctrl+D
- **Column Selection**: Shift+Alt+Drag

---

## 🔄 **8. Version Control Integration**

### **Git Workflow in VS Code**
1. **Source Control Panel**: Ctrl+Shift+G
2. **View Changes**: Click files to see diff
3. **Stage Changes**: Click + next to files or stage all
4. **Commit**: Enter commit message and Ctrl+Enter
5. **Push/Pull**: Use GitLens status bar icons

### **Branch Management**
- **Current Branch**: Shown in status bar (bottom left)
- **Switch Branches**: Click branch name in status bar
- **Create Branch**: Command Palette (Ctrl+Shift+P) → "Git: Create Branch"
- **Merge Branches**: GitLens provides visual merge tools

### **GitLens Enhanced Features**
- **Blame Annotations**: See who changed each line
- **File History**: Complete change history for files
- **Compare Revisions**: Visual diff between versions
- **Interactive Rebase**: Advanced Git operations

---

## ⚙️ **9. Customizing Your Development Environment**

### **Essential Settings for uDOS Development**
Located in `.vscode/settings.json`:

```json
{
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "editor.rulers": [80, 120],
    "editor.wordWrap": "on",
    "files.associations": {
        "*.ucode": "vb",
        "*.us": "shellscript",
        "*.md": "markdown"
    },
    "terminal.integrated.defaultProfile.osx": "zsh",
    "terminal.integrated.fontSize": 14,
    "markdown.preview.fontSize": 14,
    "markdown.preview.lineHeight": 1.6,
    "files.exclude": {
        "**/node_modules": true,
        "**/.git": true,
        "**/backup*": true
    }
}
```

### **Custom Keyboard Shortcuts**
Add to keybindings.json:

```json
[
    {
        "key": "f5",
        "command": "workbench.action.tasks.runTask",
        "args": "Run uCode Script"
    },
    {
        "key": "ctrl+shift+t",
        "command": "workbench.action.tasks.runTask",
        "args": "Test uCode Script"
    },
    {
        "key": "ctrl+shift+d",
        "command": "workbench.action.tasks.runTask",
        "args": "Deploy Script"
    }
]
```

### **Custom Themes for uDOS Development**
Recommended themes that work well with uCode syntax:

- **Dark+** (default) - Good contrast for long coding sessions
- **Monokai** - Popular theme with excellent uCode highlighting
- **One Dark Pro** - Easy on the eyes with good color differentiation
- **Material Theme** - Modern, clean appearance

---

## 📊 **10. Productivity Tips and Tricks**

### **Workspace Management**
- **Multiple Workspaces**: Use File → Add Folder to Workspace
- **Workspace Switching**: Ctrl+R for recent workspaces
- **Split Editors**: Ctrl+\ to view multiple files side-by-side
- **Editor Groups**: Organize related files in groups

### **Terminal Productivity**
- **Multiple Terminals**: Split terminal for different tasks
- **Terminal Profiles**: Pre-configured for uDOS development
- **Task Integration**: Run uDOS tasks directly from terminal
- **Shell Integration**: Access uDOS commands from terminal

### **Search and Replace Power**
- **Regex Search**: Enable regex in search (Alt+R)
- **Search in Selection**: Select text first, then search
- **Replace in Files**: Ctrl+Shift+H for project-wide replace
- **Search Filters**: Use file type filters (!*.md to exclude markdown)

### **Code Organization**
- **Folding**: Collapse code sections for better overview
- **Minimap**: Enable for large file navigation
- **Breadcrumbs**: Show file path and symbols
- **Outline View**: Navigate by functions and sections

---

## 🚨 **11. Troubleshooting Common Issues**

### **Script Execution Problems**

#### **Script Not Running**
```bash
# Check file permissions
chmod +x /path/to/script.ucode

# Verify uCode interpreter path
which ucode-modular.sh

# Test with verbose output
./uCORE/code/ucode-modular.sh DEBUG_SCRIPT YourScript
```

#### **Syntax Errors**
1. Check VS Code **Problems** panel (Ctrl+Shift+M)
2. Look for red underlines in editor
3. Use uCode syntax validator: `TEST_SCRIPT` command
4. Check parentheses, quotes, and block endings

### **VS Code Performance Issues**

#### **Slow Performance**
1. **Disable unused extensions**: Extensions → Disable
2. **Exclude large directories**: Add to `files.exclude` in settings
3. **Use workspace-specific settings**: Don't apply globally
4. **Restart VS Code**: Sometimes memory builds up

#### **High Memory Usage**
1. Close unused tabs and editors
2. Disable file watchers for large directories
3. Use "TypeScript and JavaScript Language Features" → Disable for non-JS projects

### **Git and Version Control Issues**

#### **Authentication Problems**
```bash
# Configure Git user information
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set up SSH keys for authentication
ssh-keygen -t ed25519 -C "your.email@example.com"
```

#### **Merge Conflicts**
1. Use VS Code's built-in merge editor
2. GitLens provides visual conflict resolution
3. Accept incoming/current changes with buttons
4. Test resolved conflicts before committing

### **uDOS-Specific Issues**

#### **uCode Syntax Not Highlighting**
1. Check file extension is `.ucode`
2. Verify language association in settings
3. Install/reinstall uDOS VS Code extension
4. Reload window: Ctrl+Shift+P → "Developer: Reload Window"

#### **Tasks Not Working**
1. Check `.vscode/tasks.json` configuration
2. Verify paths to uDOS scripts
3. Test commands manually in terminal first
4. Check terminal shell configuration

---

## 🎓 **12. Next Steps and Advanced Topics**

### **Mastering uDOS Development**
1. **Study Existing Scripts**: Explore `/uSCRIPT/library/ucode/`
2. **Read Documentation**: Review all files in `/docs/`
3. **Contribute to Project**: Submit improvements and new features
4. **Join Community**: Participate in uDOS development discussions

### **Advanced Development Techniques**
- **Multi-file Projects**: Organize complex scripts across multiple files
- **Configuration Management**: Use JSON configs for flexibility
- **Testing Frameworks**: Develop comprehensive test suites
- **Performance Optimization**: Profile and optimize script performance

### **Integration Opportunities**
- **CI/CD Pipelines**: Automate testing and deployment
- **External APIs**: Integrate with web services and databases
- **Custom Extensions**: Develop VS Code extensions for uDOS
- **Documentation Generation**: Auto-generate docs from code

---

## 📚 **Resources and References**

### **VS Code Documentation**
- [VS Code User Guide](https://code.visualstudio.com/docs)
- [VS Code Keyboard Shortcuts](https://code.visualstudio.com/shortcuts/keyboard-shortcuts-macos.pdf)
- [VS Code Extensions](https://marketplace.visualstudio.com/vscode)

### **uDOS Documentation**
- **uCode Developer Guide**: `/docs/uCode-Developer-Guide.md`
- **uDOS Concepts**: `/docs/uDOS-Concepts-v1.3.md`
- **Architecture Guide**: `/docs/ARCHITECTURE.md`
- **User Guide**: `/docs/USER-GUIDE.md`

### **Git and Version Control**
- [Git Documentation](https://git-scm.com/doc)
- [GitLens Extension](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)
- [GitHub Desktop](https://desktop.github.com/) (alternative GUI)

---

```ascii
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     🚀 Welcome to uDOS Development with VS Code! 🚀                        ║
║                                                                              ║
║   This guide provides everything you need to become productive with uDOS    ║
║   development using VS Code. Start with the Quick Start checklist, then     ║
║   explore the advanced features as you become more comfortable with the     ║
║   environment.                                                              ║
║                                                                              ║
║          🎯 Happy coding with uDOS! 🎯                                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

**Document Version**: 1.0  
**Last Updated**: August 17, 2025  
**Target Audience**: Wizard Installation Dev Mode Users  
**Maintenance**: Update with new VS Code features and uDOS developments

**Quick Help**: For immediate assistance, check the VS Code **Help** menu or press **F1** for the Command Palette.
