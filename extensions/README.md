# uDOS Extensions v1.3

The uDOS extension system provides modular functionality expansion through a clean plugin architecture distributed across logical locations.

## Extension Architecture

### Current Structure
```
extensions/                    # System-wide extensions
├── README.md                  # This file
└── gemini/                    # Gemini AI Integration
    ├── manifest.json
    ├── udos-gemini.sh
    ├── context/
    ├── reasoning/
    └── profiles/

uSCRIPT/extensions/           # Script-related extensions
├── extensions.sh             # Extension manager
├── registry.json             # Extension registry
├── deployment-manager.sh     # Deployment system
├── smart-input-enhanced.sh   # Enhanced input system
└── templates/

wizard/vscode/                # Development extensions
├── .vscode/                  # VS Code settings
└── vscode-extension/         # uDOS VS Code Extension
    ├── package.json
    ├── snippets/
    ├── src/
    └── syntaxes/
```

### Registry System
Script extensions are registered in `uSCRIPT/extensions/registry.json` with metadata including:
- Extension ID and version
- Name and description  
- Category classification
- Configuration requirements
- Installation status

## Available Extensions

### System Extensions (extensions/)

#### 1. Gemini AI Integration (`gemini`)
**Version:** 1.0.0  
**Purpose:** AI-powered assistance and context awareness

##### Features:
- **Context Integration**: Automatic context collection and processing
- **Reasoning Engines**: Role-specific AI reasoning (ghost, drone, imp)
- **Profile Management**: Sorcerer and other role-specific profiles
- **Command Integration**: uCode command enhancement
- **Auto-updates**: Intelligent context refresh and maintenance

##### Usage:
```bash
# Access Gemini features through uCode commands
🌀 GEMINI context update
🌀 GEMINI reasoning drone
🌀 GEMINI profile sorcerer
```

### Script Extensions (uSCRIPT/extensions/)

### Script Extensions (uSCRIPT/extensions/)

#### 1. Deployment Manager (`deployment-manager`)
**Version:** 1.0.0  
**Purpose:** Comprehensive deployment system for multiple installation types

##### Features:
- **Drone Installations**: Lightweight remote deployments with minimal footprint
- **Standalone Installations**: Complete self-contained uDOS systems
- **Server Installations**: Multi-user server deployments with API support
- **Portable Installations**: USB/removable media optimized packages
- **Template System**: JSON-based deployment configuration templates
- **Validation Engine**: Automatic deployment verification

##### Usage:
```bash
# List deployment options
./uSCRIPT/extensions/extensions.sh RUN deployment-manager LIST

# Deploy a drone installation
./uSCRIPT/extensions/extensions.sh RUN deployment-manager DRONE /path/to/target

# Deploy standalone installation
./uSCRIPT/extensions/extensions.sh RUN deployment-manager STANDALONE /path/to/install

# Create portable installation
./uSCRIPT/extensions/extensions.sh RUN deployment-manager PORTABLE /media/usb
```

##### Templates:
- `minimal-drone.json`: Basic drone configuration
- `standard-installation.json`: Full standalone setup
- `server-deployment.json`: Multi-user server config
- `portable-package.json`: USB-optimized package

#### 2. Smart Input Enhanced (`smart-input-enhanced`)
**Version:** 2.0.0  
**Purpose:** Advanced input collection with AI suggestions and form builders

##### Features:
- **Enhanced Validation**: 12+ input types with smart validation
- **Form Builder**: Interactive form creation with JSON export
- **Wizard System**: Multi-step guided workflows
- **Context-Aware Suggestions**: Dynamic input recommendations
- **Rich UI**: Colored prompts, symbols, and enhanced user experience
- **Multi-Selection Support**: Single and multiple choice inputs

##### Usage:
```bash
# Show available features
./uSCRIPT/extensions/extensions.sh RUN smart-input-enhanced LIST

# Create interactive form
./uSCRIPT/extensions/extensions.sh RUN smart-input-enhanced FORM CREATE "contact-form"

# Run mission creation wizard
./uSCRIPT/extensions/extensions.sh RUN smart-input-enhanced WIZARD mission-creation

# Smart prompt with validation
./uSCRIPT/extensions/extensions.sh RUN smart-input-enhanced PROMPT "Enter email" email
```

##### Input Types:
- **Basic**: text, number, float, alphanum
- **Formatted**: email, url, phone, date, time
- **System**: filename, path, json
- **Interactive**: select, multiselect, checkbox, textarea

##### Wizards:
- `mission-creation`: Step-by-step mission planning
- `project-setup`: Project initialization guide
- `template-builder`: Custom template creation
- `system-config`: System configuration wizard

### Development Extensions (wizard/vscode/)

#### 1. uDOS VS Code Extension (`vscode-extension`)
**Version:** 1.0.0  
**Purpose:** Enhanced VS Code support for uDOS development

##### Features:
- **Syntax Highlighting**: uSCRIPT and uDOS file support
- **Code Snippets**: Pre-built snippets for common patterns
- **IntelliSense**: Auto-completion for uDOS commands
- **Debugging Support**: Integrated debugging for uSCRIPT
- **Project Templates**: Quick project setup templates

##### Files:
- `snippets/uscript.json`: uSCRIPT language snippets
- `snippets/udos-enhanced.json`: Enhanced uDOS snippets
- `syntaxes/`: Language syntax definitions
- `src/`: Extension source code

## Extension Management

### Loading Script Extensions
```bash
# List all available script extensions
./uSCRIPT/extensions/extensions.sh LIST

# Run specific script extension
./uSCRIPT/extensions/extensions.sh RUN <extension-id> [args...]
```

### System Extensions
System extensions (like Gemini) are integrated directly into the uDOS core system and accessed through standard uCode commands.

### Development Extensions
Development extensions are automatically available in the wizard environment when using VS Code.

### Extension Registry
Script extensions are tracked in `uSCRIPT/extensions/registry.json`:
- Extension metadata and versions
- Configuration requirements
- Installation status
- Dependencies and compatibility

### Development
Script extensions are developed in `uSCRIPT/extensions/` and follow these conventions:
- Script naming: `<extension-id>.sh`
- Must be executable (`chmod +x`)
- Self-contained with metadata headers
- Support standard command patterns (LIST, HELP, etc.)

## Integration with uDOS

### Core Integration
Extensions integrate with core uDOS components:
- **uMEMORY**: Store forms, deployment configs, logs
- **wizard**: Development workflow integration
- **uKNOWLEDGE**: Template and configuration storage
- **Logging**: Centralized action logging

### Template System
Extensions utilize uDOS template system for:
- Deployment configurations
- Form definitions
- Workflow templates
- System configurations

### Workflow Integration
Extensions work with wizard workflows for:
- Automated deployment processes
- Form-driven data collection
- Template-based project setup
- System maintenance tasks

## Future Extensions

### Planned Extensions:
- **Cloud Deployment Manager**: AWS, Azure, GCP integration
- **Developer Tools**: Enhanced development environment setup
- **Backup & Sync**: Automated backup and synchronization
- **API Extensions**: REST API generation and management
- **Monitoring Tools**: System health and performance monitoring

### Extension Framework:
- Plugin API for third-party extensions
- Extension marketplace and discovery
- Automatic updates and dependency management
- Cross-extension communication protocols

## Migration Notes

### From Legacy Components:
- **uCORE/extensions/** → Reorganized into logical locations
- **drone-management.sh** → `deployment-manager` extension
- **smart-input.sh** → Enhanced in `smart-input-enhanced` extension
- Core functionality preserved and expanded
- Backward compatibility maintained where possible

### Configuration Migration:
- Legacy configs moved to appropriate extension locations
- New distributed extension system
- Template-driven setup replacing hardcoded configurations
- Role-based extension access and management

## Best Practices

### Extension Development:
1. Follow naming conventions (`extension-id.sh`)
2. Place extensions in appropriate locations by purpose
3. Include metadata headers with version info
4. Implement standard commands (LIST, HELP)
5. Use uDOS logging and directory conventions
6. Provide comprehensive validation and error handling

### Usage Guidelines:
1. Use appropriate extension manager for each type
2. Check extension registry for capabilities and versions
3. Use templates for consistent configurations
4. Log actions for audit trails and debugging
5. Validate inputs and outputs for system integrity

---

**Status**: Active and Distributed  
**Compatibility**: uDOS v1.3+  
**Architecture**: Reorganized for logical distribution  
**Last Updated**: August 17, 2025
