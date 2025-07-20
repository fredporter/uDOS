# uDOS VS Code Extension v1.2.0

**Official VS Code extension for uDOS v1.2 - Universal Development & Operations System**

The VS Code extension provides native IDE support for uDOS development with unified architecture, OK-Assistant integration, and comprehensive template management.

## 🏗️ System Integration

The extension serves as the official IDE integration layer for uDOS v1.2:
- **Template System**: Integration with unified template collection
- **OK-Assistant**: Support for configurable AI assistants (Chester, generic, etc.)
- **Command Interface**: Direct access to unified ucode.sh command system
- **Memory System**: Integration with flat file memory structure
- **Mapping System**: Access to uMapping geographic data and tools

## 🚀 Features

### 📝 Template & Content Support
- **Template Gallery**: Browse and use all uDOS templates
- **OK-Assistant Templates**: Generate scripts with assistant integration
- **Shortcode Processing**: Template variable substitution and processing
- **Live Preview**: Real-time template rendering and validation

### 🤖 Assistant Integration
- **OK-Assistant System**: Universal assistant framework
- **Chester Integration**: Full support for Chester personality profile
- **Assistant Configuration**: Switch between assistant types and personalities
- **Context-Aware Help**: Intelligent suggestions based on current work

### 🎯 Development Tools
- **uScript Language Support**: Syntax highlighting for .uscript files
- **Command Integration**: Direct access to ucode.sh unified commands
- **Memory Browser**: Navigate flat file memory structure
- **Geographic Data**: Browse uMapping datasets and coordinate systems

## 📦 Installation

### From VS Code Marketplace
```bash
# Search for "uDOS" in VS Code Extensions
# Install "uDOS v1.2.0 - Universal Development & Operations System"
```

### Manual Installation (Development)
```bash
cd extension/
npm install
npm run compile
# Install via VS Code: "Extensions: Install from VSIX"
```

## 🎯 Available Commands

### 🎯 Core uDOS v1.2
- `uDOS: Quick Setup` - Initialize uDOS workspace
- `uDOS: System Status` - Show system health and status
- `uDOS: Run Command` - Execute unified ucode.sh commands
- `uDOS: Open Memory System` - Browse flat file memory structure

### 📝 Templates & Content
- `uDOS: Create Project` - Generate project from template
- `uDOS: Create Mission` - Generate mission from template
- `uDOS: Create Milestone` - Generate milestone from template
- `uDOS: List Templates` - Browse available templates
- `uDOS: Generate Script from Template` - Create OK-Assistant scripts
- `uDOS: Process Template Shortcodes` - Execute template processing

### 🤖 Assistant System
- `uDOS: Start OK-Assistant` - Launch configurable assistant
- `uDOS: Configure Assistant` - Set assistant type and personality
- `uDOS: List Available Assistants` - Show supported assistant types

### 📊 Monitoring & Analytics  
- `uDOS: Show Live Dashboard` - Display real-time system dashboard
- `uDOS: Generate Dashboard` - Create custom dashboard views
- `uDOS: Update Analytics` - Refresh system metrics

### 🗺️ Geographic & Mapping
- `uDOS: Browse Geographic Data` - Access uMapping datasets and tools

## 🛠️ Requirements

- **VS Code**: 1.60.0 or higher
- **uDOS**: v1.2.0 installation
- **Node.js**: For extension development and compilation

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
