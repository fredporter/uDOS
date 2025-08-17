# uSCRIPT v1.3 - Production Script Library & Execution Engine

uSCRIPT v1.3 is a comprehensive production script library and execution engine for uDOS. Unlike the development-focused wizard folder, uSCRIPT is designed for managing and executing finalized, production-ready scripts across multiple programming languages.

## Purpose

uSCRIPT v1.3 serves as:
- **Production Script Library**: Repository for finalized, tested scripts
- **Multi-Language Execution Engine**: Support for Python, Shell, JavaScript, and native uCODE
- **Security-First Architecture**: Sandboxed execution with configurable security levels
- **Enterprise Script Management**: Catalog-based organization with metadata and versioning

## Key Differences from Wizard

| Aspect | uSCRIPT v1.3 | wizard/ |
|--------|--------------|---------|
| Purpose | Production script library | Development & testing |
| Script Types | Finalized, production-ready | One-off development scripts |
| Languages | Python, JS, Shell, uCODE | Primarily bash/development |
| Security | Multi-level with sandboxing | Development-focused |
| Organization | Catalog-based registry | Task-based folders |

## Directory Structure

```
uSCRIPT/
├── uscript.sh              # Main execution engine
├── README.md               # This documentation
├── config/                 # System configuration
│   ├── defaults.json       # Default execution settings
│   ├── engines.json        # Language engine configs
│   └── security.json       # Security level definitions
├── library/                # Script library organized by language/type
│   ├── python/             # Python scripts (.py)
│   ├── shell/              # Shell scripts (.sh)
│   ├── javascript/         # JavaScript/Node.js scripts (.js)
│   ├── ucode/              # Native uCODE scripts (.ucode.md)
│   ├── utilities/          # General utility scripts
│   └── automation/         # Automation and workflow scripts
├── registry/               # Script catalog and metadata
│   └── catalog.json        # Master script registry
├── runtime/                # Execution environment
│   ├── engines/            # Language-specific execution engines
│   ├── sandbox/            # Sandboxed execution environments
│   └── logs/               # Execution logs and history
└── executed/               # Archive of completed executions
```

## Security Levels

uSCRIPT v1.3 implements a three-tier security model:

- **safe**: Read-only scripts, sandboxed execution, no network/file write access
- **elevated**: File modification allowed, requires user confirmation
- **admin**: Full system access, requires admin confirmation and privileges

## Usage

### Initialize System
```bash
./uscript.sh init
```

### List Available Scripts
```bash
./uscript.sh list
```

### Get Script Information
```bash
./uscript.sh info <script-name>
```

### Execute Script
```bash
./uscript.sh run <script-name> [arguments...]
```

### Help
```bash
./uscript.sh help
```

## Supported Languages

1. **Python** (.py): Full Python 3 support with package management
2. **Shell** (.sh): Bash scripts with timeout and security controls
3. **JavaScript** (.js): Node.js execution environment
4. **uCODE** (.ucode.md): Native uDOS script format (coming soon)

## Configuration

All system behavior is controlled through JSON configuration files:

- `config/defaults.json`: Default execution parameters
- `config/engines.json`: Language engine configurations
- `config/security.json`: Security level definitions and restrictions
- `registry/catalog.json`: Master script catalog with metadata

## Script Development

Scripts in uSCRIPT should be:
- **Production-ready**: Thoroughly tested and documented
- **Properly cataloged**: Registered in catalog.json with complete metadata
- **Security-conscious**: Assigned appropriate security levels
- **Well-documented**: Include parameter descriptions and usage examples

## Version History

- **v1.3.0** (2025-08-17): Complete redesign as production script library
- **v1.2.x**: Development script manager (deprecated)
- **v1.1.x**: Basic script execution (deprecated)

