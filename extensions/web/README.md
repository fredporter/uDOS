# Typo Web Editor Integration

Web-based markdown editor for uDOS, powered by [rossrobino/typo](https://github.com/rossrobino/typo).

## Features

- **Web-Based Interface**: Edit files in your browser with live preview
- **File System API**: Modern browser API for file handling (when supported)
- **Auto-Save**: Automatically saves changes if supported by your browser
- **Markdown Support**: Full markdown editing with formatting
- **Slide Mode**: Create presentations using `---` separators
- **Code Execution**: Run JavaScript/TypeScript code blocks in-browser
- **Print Formatting**: Print formatted markdown documents

## Installation

### Automated Setup

```bash
cd extensions
./setup_typo.sh
```

The setup script will:
1. Check for Node.js and npm
2. Clone the typo repository
3. Install dependencies
4. Verify installation

### Manual Setup

1. Ensure Node.js (v16+) and npm are installed
2. Clone the repository:
   ```bash
   mkdir -p extensions/web
   cd extensions/web
   git clone https://github.com/rossrobino/typo.git
   cd typo
   npm install
   ```

## Usage

### From uDOS

#### Start the Server

```bash
🔮 server start typo
# Opens http://localhost:5173 in your browser
```

**Options:**
- `--port <number>`: Use a different port
- `--no-browser`: Don't auto-open browser

```bash
🔮 server start typo --port 3000
🔮 server start typo --no-browser
```

#### Edit Files

```bash
🔮 edit --web myfile.md
# Starts typo server if not running, opens browser
```

#### Check Status

```bash
🔮 server status typo
# Shows: Running, PID, URL, uptime
```

#### Stop the Server

```bash
🔮 server stop typo
```

#### List All Servers

```bash
🔮 server list
```

### Manual Usage

```bash
cd extensions/web/typo
npm run dev
# Opens on http://localhost:5173
```

## File Bridge (Coming Soon)

Future updates will include automatic file bridging:
- Auto-load files from uDOS when opening
- Auto-save back to uDOS filesystem
- Real-time sync between browser and disk
- URL parameter support for direct file loading

**Current Workaround:**
1. Start typo: `server start typo`
2. Manually open/save files in the web interface
3. Files must be loaded using browser's file picker

## Configuration

### Default Port

Default: `5173` (Vite development server)

Change in uDOS command:
```bash
🔮 server start typo --port 8080
```

### Server State

Server state is tracked in: `sandbox/.server_state.json`

Contains:
- PID (process ID)
- Port number
- Start time
- URL

## Troubleshooting

### Port Already in Use

```
❌ Port 5173 is already in use
```

**Solution:** Use a different port or stop the conflicting process
```bash
🔮 server start typo --port 5174
```

### Node.js Not Found

```
❌ Node.js not found
```

**Solution:** Install Node.js
- macOS: `brew install node`
- Linux: `sudo apt install nodejs npm`
- Windows: Download from https://nodejs.org

### Dependencies Not Installed

```
⚠️  Dependencies not installed
```

**Solution:** Reinstall
```bash
cd extensions/web/typo
npm install
```

### Server Won't Stop

```bash
# Find and kill manually
ps aux | grep "npm run dev"
kill <PID>
```

Or use force stop:
```bash
🔮 server stop typo
# If that fails, manually clean up
rm sandbox/.server_state.json
```

## Development

### Local Changes

If you modify the typo source:

```bash
cd extensions/web/typo
npm run dev  # Development mode with hot reload
npm run build  # Production build
```

### Upstream Updates

Update to latest typo version:

```bash
cd extensions/web/typo
git pull origin main
npm install
```

## Architecture

```
uDOS
 └── extensions/
      └── web/
           └── typo/
                ├── src/           # Svelte source files
                ├── static/        # Static assets
                ├── package.json   # Dependencies
                ├── vite.config.ts # Build configuration
                └── node_modules/  # Installed packages (gitignored)
```

### Integration Points

1. **ServerManager** (`core/uDOS_server.py`)
   - Starts/stops npm dev server
   - Tracks process state
   - Manages ports

2. **EditorManager** (`core/uDOS_editor.py`)
   - Detects web mode
   - Calls ServerManager
   - Opens browser

3. **CommandHandler** (`core/uDOS_commands.py`)
   - `SERVER` commands
   - `EDIT --web` flag

## License

Typo is licensed under the MIT License.
See: https://github.com/rossrobino/typo/blob/main/LICENSE.md

## Links

- **Upstream Repository**: https://github.com/rossrobino/typo
- **Live Demo**: https://typo.robino.dev
- **Component Library**: https://drab.robino.dev
