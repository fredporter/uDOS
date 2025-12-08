# uDOS VS Code Extension

Language support for uDOS .uPY scripting language with syntax highlighting, IntelliSense, debugging, sandbox testing, and knowledge quality tools.

## Features

### 🎨 Syntax Highlighting
- **Keywords**: Control flow (IF, FOREACH, WHILE), system (SET, GET), directives (#BREAK, #DEBUG)
- **Commands**: 60+ uDOS commands color-coded by category
- **Variables**: System variables ($MISSION, $WORKFLOW, $LOCATION) with property completion
- **Strings**: Double and single quotes with escape sequences
- **Comments**: Line comments with `#`

### 💡 IntelliSense (Autocomplete)
- **Command Completion**: All 60+ uDOS commands with usage examples
- **Variable Completion**: System variables and properties
- **Context-Aware**: Triggers on `.` for properties, space for commands
- **Documentation**: Inline docs for every command

### 📖 Hover Documentation
- **Command Help**: Comprehensive documentation on hover
- **Variable Info**: Details for all system variables
- **Examples**: Real-world usage examples

### ✂️ Code Snippets
- `mission` - Complete mission template
- `workflow` - Workflow template
- `foreach` - For-each loop
- `while` - While loop
- `if` - If-then-else conditional
- `guide` - Create knowledge guide
- `map` - Map navigation
- `checkpoint` - Save/restore checkpoint
- `gen-guide` - Generate knowledge with AI
- `gen-diagram` - Generate SVG diagram
- `try` - Error handling
- `batch` - Batch processing with progress
- `header` - File header with metadata
- `debug` - Debug output
- `cleanup` - Cleanup handler

### 🧪 Sandbox Testing
- **Isolated Instances**: Run scripts in disposable uDOS environments
- **Safe Testing**: No impact on production data
- **Auto-Cleanup**: Sandbox files removed after execution
- **Comparison**: Compare sandbox vs production results

### 🐛 Script Execution & Debugging
- **Run Script**: Execute .upy files directly from VS Code
- **Debug Panel**: View output, variables, execution time
- **Breakpoint Support** (planned)
- **Variable Inspection**: Real-time variable values

### 📚 Knowledge Quality Checker
- **Scan 228 Guides**: Automatic quality analysis
- **Flag Issues**: Outdated content, missing frontmatter, broken links
- **REGEN Recommendations**: Generate batch REGEN commands
- **Quality Metrics**: Word count, examples, cross-references

### 🎨 Image Format Validation
- **SVG Inspector**: Validate SVG diagrams, check structure
- **ASCII Tester**: Verify ASCII art consistency
- **Teletext Validator**: Check teletext page format (24×40)
- **Visual Preview**: Render images in VS Code panels

## Installation

### From Source (Development)

1. **Prerequisites**:
   ```bash
   node >= 18.0.0
   npm >= 9.0.0
   ```

2. **Clone and Install**:
   ```bash
   cd extensions/vscode-udos
   npm install
   ```

3. **Compile**:
   ```bash
   npm run compile
   # or watch mode
   npm run watch
   ```

4. **Install in VS Code**:
   - Press `F5` to launch Extension Development Host
   - Or package: `npm run package` → Install `.vsix` file

### From Marketplace (Future)

```
Search "uDOS Language Support" in VS Code Extensions
```

## Usage

### Basic Editing

1. **Create .upy file**:
   ```upy
   # water-filter-guide.upy
   MISSION CREATE "Water Filter Construction"
   GUIDE ADD tier3 guide "DIY Water Filter"
   MAP GOTO AA340 100
   MISSION COMPLETE
   ```

2. **Get IntelliSense**:
   - Type command name → suggestions appear
   - Press `Ctrl+Space` for manual trigger
   - Hover over commands for documentation

3. **Use Snippets**:
   - Type `mission` → press `Tab`
   - Fill in placeholders
   - Navigate with `Tab`/`Shift+Tab`

### Running Scripts

**Method 1: Command Palette**
```
Ctrl+Shift+P → "uDOS: Run Script"
```

**Method 2: Right-Click Menu**
```
Right-click in .upy file → "uDOS: Run Script"
```

**Method 3: Editor Title Icon**
```
Click ▶️ icon in editor title bar
```

### Sandbox Testing

**Run in Sandbox**:
```
Ctrl+Shift+P → "uDOS: Run in Sandbox"
```

Creates isolated uDOS instance:
- Fresh memory directory
- No impact on production
- Auto-cleanup after execution
- Compare results with production

### Knowledge Quality Check

**Run Quality Scan**:
```
Ctrl+Shift+P → "uDOS: Check Knowledge Quality"
```

Generates report:
- Total guides: 228
- Issues found: broken links, missing frontmatter, outdated
- Guides flagged for REGEN
- Quality metrics

### Image Validation

**Preview SVG**:
```
Right-click .svg file → "uDOS: Preview SVG"
```

**Preview ASCII**:
```
Select ASCII art → Ctrl+Shift+P → "uDOS: Preview ASCII Art"
```

**Validate Teletext**:
```
Open .teletext file → Ctrl+Shift+P → "uDOS: Validate Teletext"
```

## Configuration

### Extension Settings

```json
{
  "udos.apiUrl": "http://localhost:5001",
  "udos.autoRunOnSave": false,
  "udos.sandboxAutoCleanup": true,
  "udos.showExecutionTime": true
}
```

### uDOS API Server

Extension requires uDOS API server running:

```bash
# In uDOS terminal
POKE API start

# Verify
curl http://localhost:5001/api/status
```

## Development

### Project Structure

```
extensions/vscode-udos/
├── package.json              # Extension manifest
├── tsconfig.json             # TypeScript config
├── language-configuration.json
├── syntaxes/
│   └── upy.tmLanguage.json   # Syntax grammar
├── snippets/
│   └── upy.json              # Code snippets
└── src/
    ├── extension.ts          # Main entry point
    ├── providers/
    │   ├── completion.ts     # IntelliSense
    │   └── hover.ts          # Hover docs
    └── commands/
        ├── executor.ts       # Script execution
        ├── sandbox.ts        # Sandbox testing
        ├── knowledge-checker.ts  # Quality check
        └── image-validator.ts    # Image validation
```

### Building

```bash
# Compile TypeScript
npm run compile

# Watch mode (auto-compile)
npm run watch

# Run tests
npm run test

# Lint
npm run lint

# Package extension
npm run package  # Creates .vsix file
```

### Testing

```bash
# Run extension in debug mode
Press F5 in VS Code

# Extension Host opens with extension loaded
# Create test .upy file
# Test features
```

## Troubleshooting

### Extension Not Activating

**Problem**: Extension doesn't activate when opening .upy files

**Solutions**:
1. Check file extension is `.upy` (not `.uPY` or `.Upy`)
2. Reload VS Code: `Ctrl+Shift+P` → "Reload Window"
3. Check extension enabled: Extensions panel → uDOS Language Support

### IntelliSense Not Working

**Problem**: No autocomplete suggestions

**Solutions**:
1. Manual trigger: `Ctrl+Space`
2. Check language mode: Bottom-right corner should show "uPY"
3. Restart Extension Host: `Ctrl+Shift+P` → "Restart Extension Host"

### Script Execution Fails

**Problem**: "uDOS: Run Script" command fails

**Solutions**:
1. Check API server running: `POKE API status`
2. Verify API URL in settings: `udos.apiUrl`
3. Check network: `curl http://localhost:5001/api/status`
4. Review error in Output panel: View → Output → uDOS

### Sandbox Cleanup Issues

**Problem**: Sandbox files not removed

**Solutions**:
1. Enable auto-cleanup: `udos.sandboxAutoCleanup: true`
2. Manual cleanup: `CLEAN --scan` in uDOS
3. Check /tmp/udos-sandbox-* directories

## Roadmap

### v1.1.0 (Planned)
- [ ] Breakpoint debugging support
- [ ] Variable watch panel
- [ ] Call stack inspection
- [ ] Step-through execution

### v1.2.0 (Planned)
- [ ] Syntax error detection (linting)
- [ ] Code formatting
- [ ] Refactoring tools
- [ ] Symbol navigation

### v1.3.0 (Planned)
- [ ] Test runner integration
- [ ] Coverage reporting
- [ ] Performance profiling
- [ ] Git integration

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md)

## License

MIT License - See [LICENSE.txt](../../LICENSE.txt)

## Links

- [GitHub Repository](https://github.com/fredporter/uDOS)
- [Documentation](https://github.com/fredporter/uDOS/wiki/VS-Code-Extension)
- [Issue Tracker](https://github.com/fredporter/uDOS/issues)
- [uDOS Wiki](https://github.com/fredporter/uDOS/wiki)

## Acknowledgments

Built for the uDOS offline-first operating system. Special thanks to the open-source community and all contributors.

---

**Status**: v1.0.0 - Initial Release (Part of uDOS v1.2.10)
