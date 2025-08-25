# uDOS Development Environment

## 🧙‍♂️ **Wizard Role + DEV Mode Only**

This development environment is restricted to **wizard role with DEV mode activated**. 

## 📁 **Structure**

```
dev/
├── active/              # Current core development (local only)
│   ├── core/           # Core system development
│   ├── extensions/     # Extension development  
│   └── tools/          # Tool development
├── scripts/            # Development automation
│   ├── build/         # Build scripts
│   ├── test/          # Test scripts
│   ├── deploy/        # Deployment scripts
│   └── maintenance/   # Maintenance scripts
├── templates/          # Development templates (synced)
│   ├── commands/      # Command templates
│   ├── extensions/    # Extension templates
│   └── configs/       # Configuration templates
├── tools/              # Development utilities
├── roadmaps/           # Project roadmaps (synced)
├── docs/               # Architecture docs (synced)
├── copilot/            # AI assistant context (synced)
└── vscode/             # VS Code configurations (synced)
```

## 🔄 **Git Sync Policy**

### Synced with Git (Team Collaboration)
- `templates/` - Development templates
- `docs/` - Architecture documentation
- `roadmaps/` - Project planning
- `copilot/instructions/` - AI assistant guidelines
- `vscode/configs/` - Shared VS Code settings

### Local Only (Not Synced)
- `active/` - Current development work
- `tools/temp-*` - Temporary utilities
- `scripts/maintenance/temp-*` - Temporary maintenance scripts

## 🛠️ **Integration Points**

### AI Assistant Integration
- `.github/copilot-instructions.md` - Main AI instructions
- `dev/copilot/` - Development-specific context
- Templates and examples for consistent development

### VS Code Integration
- `.vscode/` - Main VS Code configuration
- `dev/vscode/` - Development-specific configurations
- Custom tasks for core development workflow

### Role-Based Access
- **Wizard + DEV**: Full access to `/dev` environment
- **All others**: Use `/sandbox` for development work
- Sandbox work is flushable, dev work is persistent

## 🚀 **Development Workflow**

### Core System Development
1. Work in `dev/active/core/`
2. Use `dev/scripts/build/` for building
3. Test with `dev/scripts/test/`
4. Deploy with `dev/scripts/deploy/`

### Extension Development
1. Use templates from `dev/templates/extensions/`
2. Develop in `dev/active/extensions/`
3. Test with extension manager
4. Deploy to `extensions/` when ready

### Documentation
1. Architecture docs in `dev/docs/`
2. API documentation auto-generated
3. Contributing guidelines maintained

## ⚠️ **Important Notes**

- DEV mode required for core system modifications
- Regular users work in `/sandbox` (flushable workspace)
- Archive important work from sandbox to permanent locations
- Follow development templates for consistency
- Use provided build and test scripts

---

**Remember**: This is a protected development environment. Experimental work should happen in `/sandbox` until ready for core integration.
