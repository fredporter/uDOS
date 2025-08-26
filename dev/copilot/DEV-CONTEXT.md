# uDOS Development Context for AI Assistants

## Development Environment
This `/dev` folder is the core development environment for uDOS, accessible only to wizard role with DEV mode activated.

## Structure
- `active/` - Current core development projects
- `scripts/` - Development automation scripts
- `templates/` - Core system templates
- `tools/` - Development utilities
- `roadmaps/` - Project planning and roadmaps
- `docs/` - Architecture and API documentation
- `copilot/` - AI assistant context and instructions
- `vscode/` - VS Code development configurations

## Role Access
- **Wizard + DEV mode**: Full access to all development tools
- **All other roles**: Use `/sandbox` for user development

## Integration Points
- `.github/copilot-instructions.md` - Main AI instructions
- `.vscode/` - VS Code development environment
- `/dev/copilot/` - Development-specific AI context
- `/sandbox/` - User workspace (flushable)
