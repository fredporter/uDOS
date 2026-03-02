# /dev/ Wiki — Development Scaffold Guide

**Welcome!** This wiki explains how to use the `/dev/` scaffold submodule to develop your own extensions, containers, and projects on top of uDOS.

> **📖 Main Entry:** [**Home**](Home.md) | [View Wiki Online](https://github.com/fredporter/uDOS-dev/wiki)

---

## Quick Navigation

| Guide | Purpose |
|-------|---------|
| [**ADD-SUBMODULE.md**](ADD-SUBMODULE.md) | Add `/dev/` to your workspace |
| [**DEVELOP-EXTENSION.md**](DEVELOP-EXTENSION.md) | Build custom extensions |
| [**DEVELOP-CONTAINER.md**](DEVELOP-CONTAINER.md) | Create container definitions |
| [**SCAFFOLD-STRUCTURE.md**](SCAFFOLD-STRUCTURE.md) | Understand the framework |
| [**API-REFERENCE.md**](API-REFERENCE.md) | uDOS API for extensions |

---

## What is `/dev/`?

The `/dev/` submodule is a **public, empty scaffold** that provides:

- ✅ **Framework structure** for organizing your work
- ✅ **Template scripts** and build configurations
- ✅ **Example code** to learn from
- ✅ **Gitignore patterns** to keep your projects private

**What it is NOT:**
- ❌ A project repository (your projects stay local)
- ❌ uDOS documentation (see `/docs/` at root)
- ❌ uDOS development workspace (this is for YOUR code)

---

## Getting Started

### 1. Add the Submodule

```bash
# In your uDOS workspace root
git submodule add https://github.com/fredporter/uDOS-dev.git dev
git submodule update --init --recursive
```

**See [ADD-SUBMODULE.md](ADD-SUBMODULE.md) for detailed instructions.**

### 2. Create Your Project

```bash
cd dev
mkdir my-extension
cd my-extension
# Start building!
```

Your project in `/dev/my-extension/` will be **automatically gitignored** — it stays private while the scaffold framework remains public.

### 3. Use the Templates

Copy and adapt from:
- `/dev/scripts/` — Automation templates
- `/dev/examples/` — Reference code
- `/dev/build/` — Build configurations

---

## Development Patterns

### Extension Development

Extensions hook into the uDOS runtime to add functionality.

**Start here:** [DEVELOP-EXTENSION.md](DEVELOP-EXTENSION.md)

**Key concepts:**
- Extension manifest (`extension.json`)
- API integration points
- Event system and hooks
- Testing your extension

### Container Development

Containers are isolated application environments with their own dependencies.

**Start here:** [DEVELOP-CONTAINER.md](DEVELOP-CONTAINER.md)

**Key concepts:**
- Container definition (`container.json`)
- Dependency management
- Lifecycle hooks
- Distribution packaging

### Local Tools & Scripts

Build automation and utilities for your workflow.

**Examples in:** `/dev/scripts/` and `/dev/tools/`

**Key concepts:**
- Task automation
- Build pipelines
- Testing utilities

---

## Keep Your Work Private

The `/dev/.gitignore` automatically excludes:

- Your project directories
- Secrets and credentials
- Build outputs
- Local configuration

**The scaffold structure itself remains tracked** so others can clone and use it too.

---

## Need Help?

### Documentation
1. **Check the guides** in this wiki
2. **Review examples** in `/dev/examples/`
3. **Read uDOS docs** in `/docs/` (root level)

### Community Support
- [**Contributing Guide**](https://github.com/fredporter/uDOS/blob/main/CONTRIBUTORS.md) — How to contribute
- [**Report Issues**](https://github.com/fredporter/uDOS/issues) — Main uDOS bugs/features
- [**Scaffold Issues**](https://github.com/fredporter/uDOS-dev/issues) — Dev scaffold problems
- [**Discussions**](https://github.com/fredporter/uDOS/discussions) — Ask questions
- [**Code of Conduct**](https://github.com/fredporter/uDOS/blob/main/CODE_OF_CONDUCT.md) — Community guidelines

---

## Contributing to the Scaffold

If you create useful templates, scripts, or examples:

1. **Remove any private/project-specific code**
2. **Make it generic** for others to adapt
3. **Submit a PR** to the [uDOS-dev repository](https://github.com/fredporter/uDOS-dev)
4. **Keep it minimal** — framework only, no projects

**For main uDOS contributions**, see the [uDOS Contributing Guide](https://github.com/fredporter/uDOS/blob/main/CONTRIBUTORS.md).

---

**Next:** [Add the submodule to your workspace →](ADD-SUBMODULE.md)
