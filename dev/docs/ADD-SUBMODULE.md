# Adding the `/dev/` Submodule to Your Workspace

This guide walks you through adding the `/dev/` scaffold submodule to your uDOS workspace so you can develop extensions, containers, and custom projects.

---

## Prerequisites

✅ Git installed and configured
✅ uDOS workspace cloned (`git clone https://github.com/fredporter/uDOS.git`)
✅ Basic understanding of git submodules

---

## Quick Start

```bash
# Navigate to your uDOS root
cd /path/to/uDOS

# Add the dev submodule
git submodule add https://github.com/fredporter/uDOS-dev.git dev

# Initialize and update
git submodule update --init --recursive

# Verify
ls dev/
# You should see: README.md, wiki/, scripts/, tools/, etc.
```

---

## Step-by-Step

### 1. Navigate to Your Workspace

```bash
cd /path/to/your/uDOS
```

Make sure you're in the **root** of your uDOS workspace (where the main `.git/` folder is).

### 2. Add the Submodule

```bash
git submodule add https://github.com/fredporter/uDOS-dev.git dev
```

This creates:
- `dev/` directory with the scaffold contents
- `.gitmodules` file tracking the submodule reference

### 3. Initialize the Submodule

```bash
git submodule update --init --recursive
```

This ensures all submodule contents are pulled down properly.

### 4. Verify Installation

```bash
# Check the structure
ls -la dev/

# You should see:
# README.md, wiki/, scripts/, tools/, examples/, build/, tests/
# .gitignore, .dev/, .archive/
```

### 5. Commit the Submodule Reference

```bash
git add .gitmodules dev
git commit -m "Add dev scaffold submodule"
```

**Note:** This commits the *reference* to the submodule, not the submodule contents themselves.

---

## Working with the Submodule

### Create Your First Project

```bash
cd dev
mkdir my-extension
cd my-extension

# Create your files
touch extension.json
touch main.py
```

Your project is **automatically gitignored** thanks to `/dev/.gitignore` patterns.

### Update the Submodule

When the scaffold framework is updated:

```bash
cd dev
git pull origin main
cd ..
git add dev
git commit -m "Update dev scaffold"
```

### Keep Framework, Exclude Projects

The `.gitignore` in `/dev/` ensures:

✅ **Framework tracked:** README, wiki, templates, examples
❌ **Projects excluded:** Your custom code stays private

---

## Troubleshooting

### "fatal: 'dev' already exists in the index"

The `dev/` folder already exists. Remove it first:

```bash
rm -rf dev
git rm -r --cached dev
git submodule add https://github.com/fredporter/uDOS-dev.git dev
```

### "No submodule mapping found"

The `.gitmodules` file is missing or corrupted:

```bash
# Remove the broken reference
git rm -r --cached dev
rm -rf dev .gitmodules

# Re-add
git submodule add https://github.com/fredporter/uDOS-dev.git dev
git submodule update --init --recursive
```

### Submodule Shows Modified State

If `git status` shows `dev` as modified but you haven't changed the framework:

```bash
cd dev
git status  # Check what changed
git checkout main  # Reset to latest

# Or update to latest:
git pull origin main
```

### Can't Push My Project Code

**This is expected!** Your project code in `/dev/my-project/` is gitignored and stays local. Only commit changes to the `/dev/` **framework** (templates, wiki, examples).

---

## Advanced: Working with Multiple Repos

If you want to version your project separately:

```bash
cd dev/my-extension
git init
git remote add origin https://github.com/yourusername/my-extension.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

Now you have:
- **uDOS repo** — main project
- **uDOS-dev submodule** — scaffold framework (public)
- **my-extension repo** — your code (private)

---

## Next Steps

✅ **Read the scaffold structure:** [SCAFFOLD-STRUCTURE.md](SCAFFOLD-STRUCTURE.md)
✅ **Start building:** [DEVELOP-EXTENSION.md](DEVELOP-EXTENSION.md) or [DEVELOP-CONTAINER.md](DEVELOP-CONTAINER.md)
✅ **Review examples:** `/dev/examples/`

---

**Back to:** [Wiki home](README.md)
