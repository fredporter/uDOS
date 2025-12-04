# Enable uDOS Syntax Highlighting

The uDOS VS Code extension is now enabled via symlink.

## ✅ What Just Happened

The extension was symlinked to your VS Code extensions folder:
```
~/.vscode/extensions/udos.vscode-udos-1.0.0 → extensions/vscode-udos/
```

## 🔄 Next Step: Reload VS Code

**Press:** `Cmd+Shift+P` (or `Ctrl+Shift+P` on Windows/Linux)

**Type:** `Developer: Reload Window`

**Press:** `Enter`

## ✨ After Reload

Open any `.upy` file and you'll see:
- ✅ **Syntax highlighting** - Commands, variables, strings colored
- ✅ **Autocomplete** - Type `GUI` and see suggestions
- ✅ **Hover docs** - Hover over `GUIDE` to see documentation
- ✅ **Snippets** - Type `mission` + Tab for full template

## 🧪 Test Files

Try opening these files to test:
```bash
code memory/tests/vscode-integration-test.upy
code extensions/vscode-udos/test-examples/feature-test.upy
code core/data/templates/adventure.template.upy
```

## 🔧 Development Mode (Optional)

To work on the extension itself:
```bash
cd extensions/vscode-udos
npm run watch    # Auto-recompile on changes
```

Then press `F5` in VS Code to launch Extension Development Host.

## ❓ Troubleshooting

### Syntax highlighting not working?
1. Reload VS Code: `Cmd+Shift+P` → `Developer: Reload Window`
2. Check file extension is `.upy` (not `.uPY` or `.UPY`)
3. Check bottom-right corner of VS Code shows "uPY" as language

### Still not working?
Run the enable script again:
```bash
./extensions/vscode-udos/enable-extension.sh
```

### Want to disable?
Remove the symlink:
```bash
rm ~/.vscode/extensions/udos.vscode-udos-1.0.0
```

## 📚 Full Documentation

See `extensions/vscode-udos/README.md` for complete feature list and usage guide.

---

**Extension Status:** ✅ Enabled and ready to use after reload
