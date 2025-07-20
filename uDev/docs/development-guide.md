# uDOS Development Mode Guide

## Overview
Development mode provides additional tools and safety features for working with uDOS templates, datagets, and validation systems.

## Directory Structure
```
uDev/
├── validation/          # Validation results and reports
├── templates/           # Template development and backup
├── testing/            # Testing infrastructure and mock data
├── schemas/            # JSON schemas for validation
├── tools/              # Development utilities
└── docs/               # Documentation and guides
```

## Available Tools

### Template Validation
```bash
./tools/validate-template.sh <file-or-directory>
```

### Mock Data Generation
```bash
./tools/generate-mock-data.sh
```

### Development Testing
```bash
./tools/run-dev-tests.sh
```

### Performance Benchmarking
```bash
./tools/benchmark-performance.sh
```

## Best Practices

1. **Always validate before committing**: Use template validation tools
2. **Test with mock data**: Generate and use mock data for testing
3. **Backup templates**: Templates are automatically backed up
4. **Use schemas**: Follow JSON schema validation
5. **Performance monitoring**: Regular performance benchmarks

## Environment Variables

- `UDOS_DEV_MODE=true` - Enable development mode
- `UDOS_VALIDATION_STRICT=true` - Strict validation mode
- `UDOS_DEBUG_LOGGING=true` - Enable debug logging
- `UDOS_BACKUP_TEMPLATES=true` - Auto-backup templates
- `UDOS_SANDBOX_MODE=true` - Sandbox execution mode

## Troubleshooting

### Common Issues
1. **Permission errors**: Ensure scripts are executable
2. **Missing dependencies**: Install jq, yq, and other tools
3. **Schema validation failures**: Check against schemas in schemas/
4. **Template syntax errors**: Use validation tools before testing

### Getting Help
- Check logs in `validation/reports/`
- Review mock data in `testing/mock-data/`
- Validate against schemas in `schemas/`
- Run development tests with `tools/run-dev-tests.sh`
