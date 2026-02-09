# Contributing to uDOS (v1.3)

**Version:** v1.3.0  
**Last Updated:** 2026-02-04

Thanks for helping build uDOS. This page is the quick path; deep process lives in:
- `docs/CONTRIBUTION-PROCESS.md`

---

## Quick Start

```bash
# Clone
git clone --recurse-submodules https://github.com/fredporter/uDOS.git
cd uDOS

# Python env
python3 -m venv venv
source venv/bin/activate

# Install deps
pip install -r requirements.txt
```

---

## How to Contribute

1. Pick a scope (`core`, `wizard`, `docs`, `wiki`)
2. Make a focused change
3. Run relevant tests
4. Open a PR with a clear summary

---

## Where to Add Things

- **Docs/specs** → `docs/`
- **Beginner docs** → `wiki/`
- **Containers** → `library/` (see contribution process)

---

## PR Checklist

- Does it keep **Core offline**?
- Does it keep **Wizard local‑first**?
- Does it update **docs** when behavior changes?

---

## Help

- Start with `wiki/README.md`
- Ask in issues or discussions
- Keep it small and shippable
