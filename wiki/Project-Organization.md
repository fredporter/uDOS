# Project Organization

The uDOS project follows a structured organization that promotes modularity, clarity, and ease of maintenance.

## Directory Structure

### Core System
- `core/`: Main system components
  - Command handlers
  - Core services
  - Utility functions

### Extensions
- `extensions/`: All extension-related code
  - `bundled/`: Built-in extensions
  - `cloned/`: Third-party extensions
  - `core/`: Shared components
    - `assets/`: Static assets
    - `css/`: Core stylesheets
    - `js/`: Core JavaScript
    - `themes/`: Theme definitions
    - `docs/`: Extension documentation

### Examples & Templates
- `knowledge/demos/`: Example scripts, interactive demos, asset bundles
- `extensions/templates/`: Extension scaffolding (CLI & web templates)
  - `extensions/`: Extension templates
    - CLI extension template
    - Web extension template
  - Example scripts and usage demos

### Documentation
- `docs/`: Main documentation
  - User guides
  - API documentation
  - Planning documents
- `wiki/`: Project wiki
- `knowledge/`: Knowledge base system

### Development & Testing
- `memory/tests/`: Test suite
- `scripts/`: Utility scripts
- `output/`: Generated files

## Organization Principles

### 1. Modularity
- Each directory serves a specific purpose
- Clear separation of concerns
- Minimal dependencies between components

### 2. Documentation
- Documentation lives close to code
- Multiple formats for different needs
- Comprehensive examples

### 3. Testing
- Centralized test suite
- Integration with CI/CD
- Example-driven development

### 4. Extension System
- Clear extension template structure
- Shared core components
- Easy third-party integration

## Best Practices

### File Organization
1. Place files in appropriate directories
2. Follow naming conventions
3. Keep related files together
4. Update documentation

### Code Structure
1. Use modular design
2. Follow style guidelines
3. Include proper documentation
4. Add relevant tests

### Extension Development
1. Use provided templates
2. Follow core component guidelines
3. Include comprehensive docs
4. Add example usage

## Recent Changes

### November 2025
- Consolidated shared components into `extensions/core/`
- Moved test files to `memory/tests/`
- Reorganized extension templates
- Updated documentation structure

## See Also
- [Development Workflow](Dev-Rounds-Workflow)
- [Extension Development](Extensions-System)
- [Contributing Guidelines](Contributing)
