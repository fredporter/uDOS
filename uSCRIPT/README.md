# uSCRIPT v1.3.3 - Production Script Library & Execution Engine

uSCRIPT v1.3.3 is the modular home for advanced script features and execution engine for uDOS. This version has been cleaned and optimized for production use with organized libraries and proper package management.

## Key Features
- **Clean Organization**: Scripts organized by language and purpose
- **Package Management**: Integrated package installation and management
- **Security Levels**: Three-tier security model for safe script execution
- **Language Support**: Python, Shell, JavaScript, and uCODE formats
- **Production Ready**: Thoroughly tested and documented scripts

## Usage
- **Script Execution**: Use `./uscript.sh run <script-name>` for secure execution
- **uCODE Modules**: Access native uDOS functionality through `library/ucode/`
- **System Scripts**: Core system operations in `library/shell/system/`
- **Development Tools**: Testing modules available in `sandbox/experiments/`

## Directory Structure

```
uSCRIPT/
├── active/                  # Active development scripts
│   ├── cleanup-uknowledge.sh
│   ├── ucode-modular.sh     # Modular command system
│   └── ucode-v13.sh         # Legacy modular code
├── library/                 # Organized script library
│   ├── core/                # Core system scripts
│   ├── javascript/          # JavaScript modules
│   ├── python/              # Python scripts and modules
│   ├── shell/               # Shell scripts organized by category
│   ├── ucode/               # Native uCODE scripts and modules
│   └── user-memory/         # User memory management
├── config/                  # Configuration files
├── registry/                # Script registry and metadata
├── runtime/                 # Runtime execution environment
├── venv/                    # Python virtual environment
└── uscript.sh               # Main execution engine
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

- **v1.3.3** (2025-08-23): Cleaned and optimized structure, organized libraries
- **v1.3.2** (2025-08-22): Modularized advanced features, improved organization
- **v1.3.0** (2025-08-17): Complete redesign as production script library
- **v1.2.x**: Development script manager (deprecated)
- **v1.1.x**: Basic script execution (deprecated)

