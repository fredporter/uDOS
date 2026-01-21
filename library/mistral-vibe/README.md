# Mistral Vibe CLI - Code Container

**Container ID:** `mistral-vibe`  
**License:** Apache-2.0  
**Type:** CLI Coding Agent

## Overview

Mistral Vibe is Mistral AI's official open-source CLI coding assistant. It provides a conversational interface to your codebase, allowing natural language interaction for code exploration, modification, and development tasks.

**⚠️ WIZARD ONLY** - Requires Mistral API key and network access.

## Features

- 🤖 **Interactive Chat** - Conversational AI that understands your requests
- 🛠️ **Powerful Toolset** - File manipulation, code search, shell execution
- 📁 **Project-Aware** - Scans project structure and Git status for context
- ⚡ **Modern CLI** - Autocompletion, history, beautiful themes
- 🔧 **Configurable** - Custom models, prompts, tool permissions
- 🔒 **Safety First** - Tool execution approval system

## Installation

### One-liner (Recommended)

```bash
curl -LsSf https://mistral.ai/vibe/install.sh | bash
```

### Via pip

```bash
pip install mistral-vibe
```

### Via uv

```bash
uv tool install mistral-vibe
```

### Via uDOS Wizard

```bash
WIZARD INSTALL mistral-vibe
```

## Configuration

### API Key

Get your Mistral API key at: https://console.mistral.ai/api-keys

```bash
# Option 1: Environment variable
export MISTRAL_API_KEY="your_key_here"

# Option 2: Save to ~/.vibe/.env
echo "MISTRAL_API_KEY=your_key_here" > ~/.vibe/.env
```

### uDOS Integration

The installation creates uDOS-specific configurations:

- `~/.vibe/prompts/udos.md` - uDOS development system prompt
- `~/.vibe/agents/udos.toml` - uDOS agent configuration

Use with: `vibe --agent udos`

## Usage

### Interactive Mode

```bash
# Start session
vibe

# With uDOS agent
vibe --agent udos

# Direct prompt
vibe "Find all TODO comments in the project"
```

### In uDOS TUI

```
OK FIX <file>        # Analyze code with Vibe
OK FIX --context     # Include logs in analysis
OK ASK <question>    # Ask coding questions
```

### Key Commands

| Command | Description |
|---------|-------------|
| `@file` | Reference a file (autocomplete) |
| `!cmd` | Execute shell command directly |
| `/help` | Show slash commands |
| `Ctrl+J` | Multi-line input |
| `Shift+Tab` | Toggle auto-approve |

## Available Tools

| Tool | Description |
|------|-------------|
| `read_file` | Read file contents |
| `write_file` | Write/create files |
| `search_replace` | Find and replace in files |
| `bash` | Execute shell commands |
| `grep` | Search code (ripgrep) |
| `todo` | Track agent's work |

## Models

| Model | Best For |
|-------|----------|
| `devstral-small` | Fast dev tasks (default) |
| `devstral-2` | Complex coding |
| `codestral-latest` | Code generation |
| `mistral-large-latest` | Advanced reasoning |

## Custom Prompts

Create prompts in `~/.vibe/prompts/`:

```markdown
# ~/.vibe/prompts/my_prompt.md
You are a specialized assistant for...
```

Use with config:

```toml
# ~/.vibe/config.toml
system_prompt_id = "my_prompt"
```

## MCP Servers

Vibe supports Model Context Protocol servers:

```toml
# ~/.vibe/config.toml
[[mcp_servers]]
name = "my_server"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]
```

## uDOS Two-Realm Architecture

Vibe runs on **Wizard Server only** (Realm B):

```
┌─────────────────────────────────────────────────┐
│ Realm B: Wizard Server (Always-On)              │
│ ┌─────────────────────────────────────────────┐ │
│ │ Mistral Vibe CLI                            │ │
│ │ - Full internet access                      │ │
│ │ - API key management                        │ │
│ │ - Code analysis & generation                │ │
│ └─────────────────────────────────────────────┘ │
│                      │                          │
│                      │ Private Transport        │
│                      ▼                          │
├─────────────────────────────────────────────────┤
│ Realm A: Device Mesh (Offline)                  │
│ ┌─────────────────────────────────────────────┐ │
│ │ uDOS TUI                                    │ │
│ │ - OK FIX command → Wizard → Vibe            │ │
│ │ - Results returned via private transport    │ │
│ │ - No direct API access                      │ │
│ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## File Structure

```
library/mistral-vibe/
├── container.json      # Container manifest
├── install.sh          # Installation script
└── README.md           # This file

~/.vibe/                # Vibe home directory
├── config.toml         # Main configuration
├── .env                # API keys
├── prompts/            # Custom prompts
│   └── udos.md         # uDOS prompt
├── agents/             # Agent configurations
│   └── udos.toml       # uDOS agent
├── tools/              # Custom tools
└── logs/               # Session logs
```

## Resources

- [GitHub Repository](https://github.com/mistralai/mistral-vibe)
- [Mistral API Console](https://console.mistral.ai)
- [Mistral Documentation](https://docs.mistral.ai)

## License

Apache-2.0 - See [LICENSE](https://github.com/mistralai/mistral-vibe/blob/main/LICENSE)
