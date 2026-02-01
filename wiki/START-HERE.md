# 👋 START HERE — uDOS Getting Started

**Welcome!** This guide gets you up and running with uDOS in 5 minutes.

> 💡 **New to uDOS?** Read this first. Then pick what you want to do from the section below.

---

## ⚡ Quick Setup (2 minutes)

### 1. Install uDOS

```bash
# Clone repository
git clone --recurse-submodules https://github.com/fredporter/uDOS.git
cd uDOS

# Setup Python environment
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install
pip install -r requirements.txt
```

### 2. Launch It

```bash
python uDOS.py    # Start the TUI
```

### 3. Explore

```
STATUS              # See what's installed
HELP                # See all commands
WIZARD start        # Start the server (if available)
```

---

## 🎯 What Do You Want to Do?

### 👤 I'm a **User**

Start here:
1. [**QUICKSTART.md**](../QUICKSTART.md) — 5-minute walkthrough
2. [**ARCHITECTURE.md**](ARCHITECTURE.md) — Understand the design
3. [**CONFIGURATION.md**](CONFIGURATION.md) — Set up your system
4. [**HELP-COMMAND-QUICK-REF.md**](HELP-COMMAND-QUICK-REF.md) — Command reference

---

### 🛠️ I'm a **Developer**

Start here:
1. [**QUICKSTART.md**](../QUICKSTART.md) — Get the code running
2. [**CONTRIBUTING.md**](CONTRIBUTING.md) — How to contribute
3. [**ARCHITECTURE.md**](ARCHITECTURE.md) — How the system works
4. [**STYLE-GUIDE.md**](STYLE-GUIDE.md) — Code standards

Then dive into:
- **Core TUI** → [uCODE.md](../docs/specs/uCODE.md)
- **Server/API** → Check [/wizard/README.md](../wizard/README.md)
- **Database** → [DATABASE-ARCHITECTURE.md](DATABASE-ARCHITECTURE.md)
- **Filesystem** → [FILESYSTEM-ARCHITECTURE.md](FILESYSTEM-ARCHITECTURE.md)

---

### 🎵 I'm Working on **Groovebox**

1. [**GROOVEBOX-PLAYBACK.md**](GROOVEBOX-PLAYBACK.md) — Music playback guide
2. [**CORE-CAPABILITIES-v1.0.7.md**](CORE-CAPABILITIES-v1.0.7.md) — What's built
3. Check [/groovebox/README.md](../groovebox/README.md) — Code structure

---

### 🧙 I'm Working on **Wizard** (Server/Plugins)

1. [**CONFIGURATION.md**](CONFIGURATION.md) — System setup
2. [**CORE-CAPABILITIES-v1.0.7.md**](CORE-CAPABILITIES-v1.0.7.md) — Features
3. Check [/wizard/README.md](../wizard/README.md) — Code structure

---

### 📚 I Want to **Learn the Architecture**

Read in this order:
1. [**ARCHITECTURE.md**](ARCHITECTURE.md) — Big picture
2. [**LAYER-ARCHITECTURE.md**](LAYER-ARCHITECTURE.md) — Grid system
3. [**FILESYSTEM-ARCHITECTURE.md**](FILESYSTEM-ARCHITECTURE.md) — File organization
4. [**DATABASE-ARCHITECTURE.md**](DATABASE-ARCHITECTURE.md) — Data storage
5. [**KNOWLEDGE-LINKING-SYSTEM.md**](KNOWLEDGE-LINKING-SYSTEM.md) — Document linking

---

## 📍 Navigation

- **Back to Root:** [README.md](../README.md)
- **Full Wiki:** [README.md](README.md)
- **Installation Guide:** [INSTALLATION.md](../INSTALLATION.md)
- **All Docs:** [docs/README.md](../docs/README.md)

---

## ❓ Common Questions

**Q: What's uDOS?**
A: An offline-first OS layer for knowledge systems, built with Python and TypeScript.

**Q: Does it work without internet?**
A: Yes! uDOS is designed for air-gapped environments.

**Q: What platforms does it support?**
A: Alpine Linux (primary), macOS, Ubuntu, Windows

**Q: How do I report a bug?**
A: See [CONTRIBUTING.md](CONTRIBUTING.md)

**Q: Where are the command references?**
A: [HELP-COMMAND-QUICK-REF.md](HELP-COMMAND-QUICK-REF.md) or run `HELP` in the TUI

---

## 🚀 Next Steps

1. ✅ Follow **Quick Setup** above
2. ✅ Pick your role (User/Developer/Musician/etc)
3. ✅ Read the recommended docs
4. ✅ Try commands in the TUI
5. ✅ Check [CONTRIBUTING.md](CONTRIBUTING.md) when you're ready to contribute

**Happy exploring!** 🎉
