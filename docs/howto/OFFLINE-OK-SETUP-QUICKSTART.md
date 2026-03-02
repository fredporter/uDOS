# Offline OK Setup Quickstart

Updated: 2026-03-03
Status: active how-to

## Purpose

Use this guide to get an offline-first OK setup running quickly with:
- local Ollama models
- optional OpenRouter burst routing through Wizard

## Quick Path

### 1. Install and start Ollama

```bash
# macOS
brew install ollama
brew services start ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
```

Verify:

```bash
curl http://127.0.0.1:11434/api/tags
```

### 2. Pull a local model

Recommended starter model:

```bash
ollama pull mistral:small
ollama run mistral:small "Hello"
```

### 3. Configure the local model path

Set the local model in `.vibe/config.toml`:

```toml
[model]
provider = "ollama"
model = "mistral:small"
endpoint = "http://127.0.0.1:11434"
cloud_enabled = false
```

### 4. Optional: enable cloud burst through Wizard

If you want fallback or burst capacity:
- create an OpenRouter account
- store the key in the Wizard secret store
- configure the Wizard OK gateway for local-first routing

### 5. Test

Test local:

```bash
vibe chat "Explain the uDOS command routing architecture"
```

Test managed/cloud path after Wizard configuration:

```bash
curl -X POST http://127.0.0.1:8765/ok/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Say hello","task_tag":"burst"}'
```

## Companion Guides

- [Offline OK Setup Reference](/Users/fredbook/Code/uDOS/docs/howto/OFFLINE-OK-SETUP-REFERENCE.md)
- [SVG Graphics Quickstart](/Users/fredbook/Code/uDOS/docs/howto/SVG-GRAPHICS-QUICKSTART.md)
- [Managed Wizard Operations](/Users/fredbook/Code/uDOS/docs/howto/MANAGED-WIZARD-OPERATIONS.md)

