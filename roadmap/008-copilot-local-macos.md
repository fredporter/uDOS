# 🚀 uDOS Developer Startup Guide: VS Code + GitHub Copilot  
**File:** 008-copilot-local-macos.md  
**Version:** Beta v1.6.1  
**Maintainer:** uDOS System  
**Created:** 2025-07-10  

## 🎯 Purpose
Set up GitHub Copilot locally on macOS using VS Code to accelerate structured Bash scripting, Markdown roadmap authoring, and uDOS move logging.

## 1. ✅ INSTALLATION STEPS

### 1.1 Install VS Code on macOS

Download from:  
[https://code.visualstudio.com/](https://code.visualstudio.com/)

After install:

```bash
code --version  # Verify CLI installed
```

If not found in terminal:

1. Open VS Code
2. Press `Cmd+Shift+P` → type `Shell Command: Install 'code' command in PATH`

---

### 1.2 Clone Your uDOS GitHub Repo

```bash
cd ~/Documents/dev  # Or your preferred workspace
git clone git@github.com:yourusername/udos.git
cd udos
code .  # Open repo in VS Code
```

---

### 1.3 Install GitHub Copilot Extension

1. Open VS Code
2. Go to **Extensions** (⇧⌘X)
3. Search for “GitHub Copilot”
4. Click **Install**
5. Sign in with your GitHub account if prompted

✅ Copilot should display `Ready` in the bottom status bar.

---

### 1.4 Disable Copilot Telemetry (Recommended)

Edit `.vscode/settings.json`:

```jsonc
{
  "github.copilot.enable": true,
  "github.copilot.inlineSuggest.enable": true,
  "github.copilot.telemetry.enable": false
}
```

---

### 1.5 Test Copilot in Bash and Markdown

Open `uCode.sh` and type:

```bash
# handle 'log move' command by writing timestamp to daily log
```

Copilot will suggest completions automatically.  
Use `Tab` or `Enter` to accept suggestions.

---

