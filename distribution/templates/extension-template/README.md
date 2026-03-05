# Example Extension

Template extension demonstrating uDOS extension system structure.

## Installation

### System Extension (Trusted)
Copy to `extensions/example/` during development or to the active runtime extension path for packaged builds.

### User Extension (Sandboxed)
Copy to `~/.udos/memory/sandbox/extensions/example/`.

## Files

- `extension.json` - Extension manifest
- `__init__.py` - Extension code
- `README.md` - This file

## Usage

```
> EXAMPLE message="Hello World!"
```

## Hooks

- `system_startup` - Called when uDOS starts
- `command_pre` - Called before any command
- `command_post` - Called after any command

## Permissions

- `filesystem:sandbox` - Access to user sandbox
- `api:commands` - Register commands

## Development

To create a new extension:

1. Copy this template directory
2. Edit `extension.json` (change id, name, description)
3. Implement handlers in `__init__.py`
4. Test in development mode
5. Package as an Alpine plugin artifact for distribution

## License

MIT
