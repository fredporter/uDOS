# VS Code Extension Troubleshooting

## Extension Crash on Launch

### Common Causes

1. **Extension Not Compiled**
   ```bash
   cd extensions/vscode-udos
   npm run compile
   ```

2. **Missing Dependencies**
   ```bash
   npm install
   ```

3. **VS Code API Version Mismatch**
   - Check `engines.vscode` in package.json matches your VS Code version
   - Current requirement: `^1.80.0`

4. **Corrupted out/ Directory**
   ```bash
   rm -rf out/
   npm run compile
   ```

### Debug Steps

1. **Check VS Code Developer Tools**
   - In Extension Development Host: `Help` → `Toggle Developer Tools`
   - Look for errors in Console tab

2. **Enable Extension Logging**
   - Open Output panel: `View` → `Output`
   - Select "uDOS Language Support" from dropdown

3. **Test Minimal Extension**
   - Comment out providers in `src/extension.ts`
   - Test activation event by event

4. **Check File Paths**
   - Ensure `language-configuration.json` exists
   - Verify `syntaxes/upy.tmLanguage.json` exists
   - Check `snippets/upy.json` exists

### Manual Testing

1. **Launch Extension Development Host**
   ```bash
   # In VS Code:
   # 1. Open extensions/vscode-udos folder
   # 2. Press F5
   # 3. New VS Code window opens with extension loaded
   ```

2. **Test Basic Features**
   - Create test file: `test.upy`
   - Type `GUIDE` - should see autocomplete
   - Hover over command - should see documentation
   - Try snippet: type `mission` + Tab

3. **Test Without API Server**
   - Extension should activate without errors
   - Commands requiring API will show friendly error
   - Syntax highlighting should work offline

### Known Limitations

- **Requires uDOS API** for script execution (commands work without it)
- **Sandbox mode** requires port 5001 available
- **Image preview** requires valid file paths

### Fix Activation Events Warning

The package.json has outdated activation events. VS Code now auto-generates these.

**Remove these lines** from `package.json`:
```json
"activationEvents": [
    "onLanguage:upy",
    "onCommand:udos.runScript",
    ...
]
```

Replace with:
```json
"activationEvents": []
```

VS Code will automatically activate on:
- Opening .upy files (from language contribution)
- Running commands (from command contribution)
