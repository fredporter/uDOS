# uCORE Extensions v1.0

The uCORE extension system provides modular functionality expansion for uDOS through a clean plugin architecture.

## Extension Architecture

### Structure
```
uCORE/extensions/
├── registry.json           # Central extension registry
├── extensions.sh          # Extension manager/loader
├── development/           # Development extensions
│   ├── deployment-manager.sh
│   └── smart-input-enhanced.sh
└── README.md             # This file
```

### Registry System
Extensions are registered in `registry.json` with metadata including:
- Extension ID and version
- Name and description
- Category classification
- Configuration requirements
- Installation status

## Available Extensions

### 1. Deployment Manager (`deployment-manager`)
**Version:** 1.0.0  
**Purpose:** Comprehensive deployment system for multiple installation types

#### Features:
- **Drone Installations**: Lightweight remote deployments with minimal footprint
- **Standalone Installations**: Complete self-contained uDOS systems
- **Server Installations**: Multi-user server deployments with API support
- **Portable Installations**: USB/removable media optimized packages
- **Template System**: JSON-based deployment configuration templates
- **Validation Engine**: Automatic deployment verification

#### Usage:
```bash
# List deployment options
./uCORE/extensions/extensions.sh RUN deployment-manager LIST

# Deploy a drone installation
./uCORE/extensions/extensions.sh RUN deployment-manager DRONE /path/to/target

# Deploy standalone installation
./uCORE/extensions/extensions.sh RUN deployment-manager STANDALONE /path/to/install

# Create portable installation
./uCORE/extensions/extensions.sh RUN deployment-manager PORTABLE /media/usb
```

#### Templates:
- `minimal-drone.json`: Basic drone configuration
- `standard-installation.json`: Full standalone setup
- `server-deployment.json`: Multi-user server config
- `portable-package.json`: USB-optimized package

### 2. Smart Input Enhanced (`smart-input-enhanced`)
**Version:** 2.0.0  
**Purpose:** Advanced input collection with AI suggestions and form builders

#### Features:
- **Enhanced Validation**: 12+ input types with smart validation
- **Form Builder**: Interactive form creation with JSON export
- **Wizard System**: Multi-step guided workflows
- **Context-Aware Suggestions**: Dynamic input recommendations
- **Rich UI**: Colored prompts, symbols, and enhanced user experience
- **Multi-Selection Support**: Single and multiple choice inputs

#### Usage:
```bash
# Show available features
./uCORE/extensions/extensions.sh RUN smart-input-enhanced LIST

# Create interactive form
./uCORE/extensions/extensions.sh RUN smart-input-enhanced FORM CREATE "contact-form"

# Run mission creation wizard
./uCORE/extensions/extensions.sh RUN smart-input-enhanced WIZARD mission-creation

# Smart prompt with validation
./uCORE/extensions/extensions.sh RUN smart-input-enhanced PROMPT "Enter email" email
```

#### Input Types:
- **Basic**: text, number, float, alphanum
- **Formatted**: email, url, phone, date, time
- **System**: filename, path, json
- **Interactive**: select, multiselect, checkbox, textarea

#### Wizards:
- `mission-creation`: Step-by-step mission planning
- `project-setup`: Project initialization guide
- `template-builder`: Custom template creation
- `system-config`: System configuration wizard

## Extension Management

### Loading Extensions
```bash
# List all available extensions
./uCORE/extensions/extensions.sh LIST

# Run specific extension
./uCORE/extensions/extensions.sh RUN <extension-id> [args...]
```

### Extension Registry
The registry tracks:
- Extension metadata and versions
- Configuration requirements
- Installation status
- Dependencies and compatibility

### Development
Extensions are developed in `uCORE/extensions/development/` and follow these conventions:
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
- **drone-management.sh** → `deployment-manager` extension
- **smart-input.sh** → Enhanced in `smart-input-enhanced` extension
- Core functionality preserved and expanded
- Backward compatibility maintained where possible

### Configuration Migration:
- Legacy configs moved to `trash/old-ucore-components/`
- New extension-based configuration system
- Template-driven setup replacing hardcoded configurations
- Centralized registry replacing scattered config files

## Best Practices

### Extension Development:
1. Follow naming conventions (`extension-id.sh`)
2. Include metadata headers with version info
3. Implement standard commands (LIST, HELP)
4. Use uDOS logging and directory conventions
5. Provide comprehensive validation and error handling

### Usage Guidelines:
1. Always use extension manager for loading extensions
2. Check extension registry for capabilities and versions
3. Use templates for consistent configurations
4. Log actions for audit trails and debugging
5. Validate inputs and outputs for system integrity

---

**Status**: Active and Expanding  
**Compatibility**: uDOS v1.3+  
**Maintainer**: wizard Workflow System  
**Last Updated**: 2024-01-15
