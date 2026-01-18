# Vibe (Devstral) Offline Agent Setup

## Overview

Mistral's **Vibe CLI** provides an offline-first AI agent using **Devstral Small 2** via Ollama. This gives uDOS a local coding assistant without cloud dependencies.

## Quick Start

```bash
# One-command setup
./Setup-Vibe.command

# Or manual steps below
```

## Prerequisites

- **macOS** (Monterey 12+) or **Linux**
- **8GB+ RAM** (16GB recommended)
- **10GB free disk space** (for model)
- **Python 3.10+** with venv

## Installation

### Automated Setup

The `Setup-Vibe.command` script handles everything:

1. Installs Ollama
2. Pulls Devstral Small 2 model (~7.7GB)
3. Starts Ollama service
4. Clones and installs Vibe CLI
5. Configures for uDOS context
6. Runs test queries

```bash
./Setup-Vibe.command
```

### Manual Installation

#### 1. Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### 2. Start Ollama Service

**macOS:**
```bash
brew services start ollama
# Or: ollama serve &
```

**Linux:**
```bash
ollama serve &
```

#### 3. Pull Devstral Model

```bash
# Pull Mistral Small 2 (Devstral)
ollama pull mistral-small2

# Verify
ollama list
```

Expected output:
```
NAME                   ID              SIZE      MODIFIED
mistral-small2:latest  abc123...       7.7 GB    2 minutes ago
```

#### 4. Install Vibe CLI

```bash
# Clone Vibe repository
mkdir -p library
cd library
git clone https://github.com/mistralai/vibe.git mistral-vibe
cd mistral-vibe

# Install to venv
source ../../.venv/bin/activate
pip install -e .

# Verify
vibe --version
```

#### 5. Configure Vibe

Configuration is already in `.vibe/config.toml`:

```toml
[model]
provider = "ollama"
model = "mistral-small2"
endpoint = "http://127.0.0.1:11434"
cloud_enabled = false

[context]
context_files = [
    "AGENTS.md",
    "docs/_index.md",
    "docs/roadmap.md",
    ".vibe/CONTEXT.md"
]
```

## Usage

### Interactive Chat

```bash
vibe chat
```

Interactive session with full uDOS context:

```
> What is the command routing architecture?
> How do I add a new command handler?
> Where are the TUI components?
> What is the version management pattern?
```

### Single Query

```bash
vibe chat "What is the uDOS transport policy?"
```

### With Context

```bash
# Vibe automatically loads .vibe/CONTEXT.md
vibe chat "Explain the three-workspace architecture"
```

### Code Assistance

```bash
vibe chat "How do I implement a new Wizard Server endpoint?"
vibe chat "Show me the handler pattern for Core commands"
vibe chat "What's the logging pattern with tags?"
```

## Configuration Files

### .vibe/CONTEXT.md

Primary context for Vibe - contains:
- Links to AGENTS.md, docs/, roadmap
- Subsystem entry points
- Architecture quick reference
- Version management rules
- Documentation patterns
- Transport policy
- Command routing flow

### .vibe/config.toml

Vibe configuration:
- Model selection (mistral-small2)
- Ollama endpoint
- Cloud disabled by default
- Context file references
- Include/exclude patterns

## Vibe vs Cloud AI

| Feature | Vibe (Local) | Cloud AI |
|---------|--------------|----------|
| **Privacy** | ✅ 100% local | ❌ Data sent to cloud |
| **Speed** | ⚡ Sub-second | 🐌 Network dependent |
| **Cost** | ✅ Free | 💰 Pay per token |
| **Offline** | ✅ Works offline | ❌ Requires internet |
| **Context** | 📁 Full repo access | 📋 Limited context |
| **Model** | Devstral Small 2 | Various (Claude, GPT, etc.) |

## Common Tasks

### Check Ollama Status

```bash
# Check if Ollama is running
ps aux | grep ollama

# Check API
curl http://127.0.0.1:11434/api/tags

# List models
ollama list
```

### Update Vibe

```bash
cd library/mistral-vibe
git pull
pip install -e .
```

### Update Model

```bash
ollama pull mistral-small2
```

### View Logs

```bash
# Ollama logs (macOS)
tail -f ~/Library/Logs/Ollama/server.log

# Ollama logs (Linux)
journalctl -u ollama -f
```

## Troubleshooting

### Ollama Not Running

```bash
# macOS
brew services start ollama

# Or manual start
ollama serve &
```

### Model Not Found

```bash
# Re-pull model
ollama pull mistral-small2

# Check available models
ollama list
```

### Vibe Command Not Found

```bash
# Activate venv
source .venv/bin/activate

# Reinstall vibe
cd library/mistral-vibe
pip install -e .
```

### Out of Memory

Devstral Small 2 requires ~8GB RAM. If you see OOM errors:

```bash
# Check available memory
free -h  # Linux
vm_stat  # macOS

# Use smaller model (if needed)
ollama pull llama3.2  # 3GB model
```

Then update `.vibe/config.toml`:
```toml
[model]
model = "llama3.2"
```

### Context Not Loading

```bash
# Verify context files exist
ls -la .vibe/
cat .vibe/CONTEXT.md

# Check config
cat .vibe/config.toml
```

## Performance Tips

### 1. Keep Ollama Running

Don't stop/start Ollama - keep it as a background service:

```bash
# macOS - auto-start on boot
brew services start ollama
```

### 2. Preload Model

First query is slower (model loads into RAM):

```bash
# Warm up the model
ollama run mistral-small2 "test"
```

### 3. Increase Context

For larger codebases, increase context window:

```toml
[model]
context_length = 8192  # default: 4096
```

### 4. Use Streaming

For interactive feel:

```bash
vibe chat --stream
```

## Integration with Dev Mode

Future enhancement - add to `Launch-Dev-Mode.command`:

```bash
dev> vibe          # Launch Vibe chat
dev> vibe-status   # Check Ollama/Vibe status
dev> vibe-update   # Update models
```

## Examples

### Architecture Questions

```bash
vibe chat "Explain the Wizard Server architecture"
vibe chat "How does command routing work in Core?"
vibe chat "What are the five markdown formats in App?"
```

### Implementation Help

```bash
vibe chat "How do I add a new command handler?"
vibe chat "Show me the logging pattern with [WIZ] tags"
vibe chat "How do I create a new transport?"
```

### Debugging Assistance

```bash
vibe chat "Where are the session command logs?"
vibe chat "How do I debug TUI errors?"
vibe chat "What's the version bump workflow?"
```

## Advanced Configuration

### Custom System Prompt

Edit `.vibe/config.toml`:

```toml
[model]
system_prompt = """
You are a uDOS development assistant. You have deep knowledge of:
- Core TUI architecture
- Wizard Server implementation
- Transport policy enforcement
- Version management system

Always reference AGENTS.md for architectural decisions.
"""
```

### Multiple Models

Switch models for different tasks:

```bash
# Code generation - use Devstral
export VIBE_MODEL=mistral-small2
vibe chat "Generate a new command handler"

# Quick questions - use Llama
export VIBE_MODEL=llama3.2
vibe chat "What port does API use?"
```

## Resources

- **Vibe GitHub:** https://github.com/mistralai/vibe
- **Ollama Docs:** https://ollama.com/docs
- **Devstral Info:** https://mistral.ai/news/devstral/
- **uDOS Context:** [.vibe/CONTEXT.md](.vibe/CONTEXT.md)
- **Wizard Model Routing:** [docs/decisions/wizard-model-routing-policy.md](../docs/decisions/wizard-model-routing-policy.md)

## Next Steps

1. ✅ Run `./Setup-Vibe.command`
2. ✅ Test with `vibe chat "What is uDOS?"`
3. ✅ Explore context with specific questions
4. ✅ Use for daily development tasks
5. 🔄 Provide feedback on model performance

---

**Version:** v1.0.0  
**Updated:** 2026-01-13  
**Status:** Ready for offline-first development! 🎉
