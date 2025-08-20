# uDOS Wizard VS Code Development Environment

## Setup Complete ✅

The VS Code workspace for uDOS wizard development is now fully configured and organized in `/Users/agentdigital/uDOS/wizard/vscode/`.

### Directory Structure
```
wizard/vscode/
├── .vscode/
│   ├── settings.json      # Workspace settings with uDOS integration
│   ├── tasks.json         # Development tasks and build commands
│   └── launch.json        # Debug configurations
├── uDOS-Wizard.code-workspace  # Multi-folder workspace file
└── vscode-extension/      # uDOS VS Code Extension source
```

### Workspace Configuration

#### Multi-Folder Workspace
- **uDOS Root**: Points to `../..` for full uDOS access
- **Wizard Development**: Points to `..` for wizard-specific work
- **VS Code Extension**: Points to `./vscode-extension` for extension development

#### Key Features
- **uDOS Integration**: Extension settings configured with correct relative paths
- **Error Handling**: Integration with wizard error handling system
- **Development Tasks**: 
  - 🌀 Start uDOS (from wizard context)
  - 🎯 Compile VS Code Extension
  - 📦 Install/Package Extension
  - 🔧 Start Wizard Logging
  - 🧪 Test Error System
  - ⚡ Run Extension Development (watch mode)

#### Debug Configurations
- **Run uDOS Extension**: Launch extension host for testing
- **Test uDOS Extension**: Run extension test suite
- **Debug uDOS Shell**: Debug uDOS shell with wizard role

### Usage

1. **Open Workspace**: 
   ```bash
   code /Users/agentdigital/uDOS/wizard/vscode/uDOS-Wizard.code-workspace
   ```

2. **Start Development**:
   - Use Cmd+Shift+P → "Tasks: Run Task" → "⚡ Run Extension Development"
   - Use F5 to launch extension for testing
   - Use Cmd+Shift+P → "Tasks: Run Task" → "🔧 Start Wizard Logging"

3. **Access uDOS**:
   - Use Cmd+Shift+P → "Tasks: Run Task" → "🌀 Start uDOS"
   - Terminal opens in uDOS root with wizard role

### Integration with Error Handling System

The workspace is fully integrated with the wizard error handling system:
- Wizard development logging available via tasks
- Error system testing capabilities
- Session management and analytics
- All role-themed error handlers accessible

### File Associations
- `.uscript`, `.us` → uScript language
- Mission files → Markdown with enhanced preview
- Template files → Markdown with enhanced preview

The workspace is ready for uDOS extension development and wizard role operations!
