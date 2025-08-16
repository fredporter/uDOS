# Google Gemini CLI Extension for uDOS

## Overview
This extension integrates the official [Google Gemini CLI](https://github.com/google-gemini/gemini-cli) into uDOS, providing two powerful AI-assisted modes:

- **ASSIST Mode**: AI-powered development assistant with full uDOS context
- **COMMAND Mode**: Natural language command interface for uDOS operations

## Features

### 🎯 ASSIST Mode
- Full uDOS project context awareness
- Code understanding and generation
- Real-time Google Search grounding
- File operations and shell commands
- Conversation checkpointing
- 1M token context window with Gemini 2.5 Pro

### 🗣️ COMMAND Mode
- Natural language command interface
- Translates speech to uDOS commands
- Interactive AI assistant for system operations
- Context-aware command suggestions
- Beginner-friendly interface

### 🔧 Integration Features
- Seamless uCode shell integration
- Automatic uDOS context loading
- Privacy-respectful configuration
- Multiple authentication options
- Offline-capable command interpretation

## Installation

### Prerequisites
- Node.js 20 or higher
- npm (comes with Node.js)
- Internet connection for initial setup

### Quick Install
```bash
cd /Users/agentdigital/uDOS/uExtensions/ai/gemini-cli
./install-gemini-cli.sh
```

### Manual Installation Steps
1. **Install Node.js** (if not already installed):
   - Download from https://nodejs.org/
   - Minimum version: 20.x

2. **Run Installation Script**:
   ```bash
   ./install-gemini-cli.sh
   ```

3. **Set Up Authentication** (see Authentication section below)

4. **Test Installation**:
   ```bash
   ./udos-gemini.sh --assist
   ```

## Authentication

### Option 1: OAuth (Recommended)
```bash
# Start ASSIST mode and follow OAuth flow
./udos-gemini.sh --assist
```
- **Benefits**: 60 requests/min, 1,000 requests/day
- **Setup**: Browser-based authentication with Google account

### Option 2: API Key
```bash
# Get API key from https://aistudio.google.com/apikey
export GEMINI_API_KEY="your-api-key-here"
./udos-gemini.sh --assist
```
- **Benefits**: 100 requests/day, specific model control
- **Setup**: Manual API key configuration

### Option 3: Vertex AI (Enterprise)
```bash
export GOOGLE_CLOUD_PROJECT="your-project"
export GOOGLE_API_KEY="your-key"
export GOOGLE_GENAI_USE_VERTEXAI=true
./udos-gemini.sh --assist
```
- **Benefits**: Enterprise features, higher limits
- **Setup**: Google Cloud Platform account required

## Usage

### ASSIST Mode
Start AI assistant with full uDOS context:
```bash
# Direct execution
./udos-gemini.sh --assist

# From uCode shell
assist

# With additional directories
./udos-gemini.sh --assist --include-directories="../custom,../projects"
```

**Example ASSIST sessions:**
```
> Analyze the current uDOS architecture and suggest improvements
> Create a new extension for file encryption
> Review the latest changes in the repository
> Help me debug the dashboard script
> Generate documentation for the template system
```

### COMMAND Mode
Natural language command interface:
```bash
# Direct execution
./command-mode.sh

# From uCode shell
command
```

**Example COMMAND interactions:**
```
uDOS-AI > start the dashboard
[COMMAND] Starting uDOS dashboard...

uDOS-AI > check system status  
[COMMAND] Checking uDOS system status...

uDOS-AI > show me available games
[AI] Interpreting: 'show me available games'
Available gaming extensions:
- NetHack (./uExtensions/gaming/nethack/)
- Adventure games (./uExtensions/gaming/adventure/)

uDOS-AI > create a new template for documentation
[AI] Interpreting: 'create a new template for documentation'
Recommended command: ./uTemplate/create-template.sh --type=documentation
```

### Quick Commands
| Command | Description |
|---------|-------------|
| `assist` | Start ASSIST mode (from uCode shell) |
| `command` | Start COMMAND mode (from uCode shell) |
| `./udos-gemini.sh --assist` | Direct ASSIST mode |
| `./command-mode.sh` | Direct COMMAND mode |

## Configuration

### Context Files
The extension automatically creates `GEMINI.md` context files to provide uDOS-specific information to the AI:

```markdown
# uDOS Project Context
You are assisting with the uDOS (Universal Data Operating System) project.

## About uDOS
- Universal Data Operating System with modular architecture
- Shell-based system with extensions for gaming, AI, development tools
- Template-driven approach with smart scripting capabilities

## Current Structure
- uCore/: Core system components
- uExtensions/: Modular extension system
- uDocs/: Documentation with location tile codes
...
```

### Environment Variables
```bash
# Gemini CLI configuration
export GEMINI_API_KEY="your-key"                    # API key authentication
export GOOGLE_CLOUD_PROJECT="project-id"            # Vertex AI project
export GOOGLE_GENAI_USE_VERTEXAI=true              # Enable Vertex AI
export GEMINI_CONTEXT_DIR="/path/to/udos"          # Context directory
```

### Settings File
Global settings stored in `~/.gemini/settings.json`:
```json
{
  "model": "gemini-2.5-pro",
  "includeDirectories": ["uCore", "uDocs", "uExtensions"],
  "contextFiles": ["GEMINI.md"],
  "theme": "default"
}
```

## Advanced Features

### MCP Server Integration
Extend functionality with Model Context Protocol servers:
```json
{
  "mcpServers": {
    "github": {
      "command": "uvx",
      "args": ["mcp-server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token"
      }
    }
  }
}
```

### Custom Tools
Add uDOS-specific tools to Gemini CLI:
```bash
> @udos list all templates
> @udos check extension status
> @udos validate installation
```

### Conversation Checkpointing
Save and resume complex sessions:
```bash
# In ASSIST mode
> /checkpoint save udos-architecture-review
> /checkpoint load udos-architecture-review
```

## Troubleshooting

### Common Issues

**Node.js Version Error**
```bash
# Check version
node --version

# Install/update Node.js from https://nodejs.org/
```

**Authentication Failed**
```bash
# Clear cached credentials
rm -rf ~/.gemini/

# Restart authentication
./udos-gemini.sh --assist
```

**Command Not Found**
```bash
# Reinstall Gemini CLI
npm uninstall -g @google/gemini-cli
npm install -g @google/gemini-cli
```

**Context Not Loading**
```bash
# Check GEMINI.md exists
ls -la GEMINI.md

# Verify uDOS root path
echo $UDOS_ROOT
```

### Debug Mode
Enable verbose logging:
```bash
export DEBUG=gemini:*
./udos-gemini.sh --assist
```

## Integration with uDOS

### uCode Shell Commands
```bash
# Available in uCode shell
assist              # Start ASSIST mode
command             # Start COMMAND mode
gemini-status       # Check Gemini CLI status
gemini-auth         # Manage authentication
```

### Dashboard Integration
The Gemini CLI extension appears in the uDOS dashboard:
```
AI Extensions:
├── Gemini CLI ✓
├── Chester Assistant ✓  
└── Custom AI Tools
```

### Template Integration
Use ASSIST mode for template operations:
```
> Create a new template for project documentation
> Generate a script template for data processing
> Help me customize the existing user manual template
```

## Distribution Support

### Included in Distribution Types
- **Developer**: Full installation with all features
- **Wizard**: Complete installation with enterprise features
- **Enterprise**: Multi-user installation with team features

### Not Included in
- **Minimal**: Too lightweight for AI features
- **Standard**: Optional installation available
- **Drone**: Offline-focused, but can be pre-configured

## Privacy and Security

### Data Handling
- No personal data transmitted without explicit user action
- Context files contain only project-specific information
- Authentication tokens stored securely by Gemini CLI
- User sandbox isolation maintained

### Network Requirements
- Internet connection required for AI requests
- Local context processing where possible
- Offline command interpretation for basic operations

## Performance

### Resource Usage
- **Memory**: ~50MB when active
- **Storage**: ~50MB installation
- **Network**: Variable based on usage
- **CPU**: Minimal background usage

### Rate Limits
- **Free OAuth**: 60 requests/min, 1,000/day
- **Free API**: 100 requests/day
- **Paid Vertex AI**: Based on billing plan

## Contributing

### Extension Development
```bash
# Clone and modify
git clone /path/to/udos
cd uExtensions/ai/gemini-cli

# Make changes
vim install-gemini-cli.sh

# Test installation
./install-gemini-cli.sh
```

### Adding Features
1. Modify integration scripts
2. Update manifest.json
3. Test with both ASSIST and COMMAND modes
4. Update documentation

## License

This extension integrates the Apache 2.0 licensed Google Gemini CLI with uDOS.

## Support

### Documentation
- [Google Gemini CLI Docs](https://github.com/google-gemini/gemini-cli/tree/main/docs)
- [uDOS Documentation](../../uDocs/)
- Extension-specific: `AUTH_SETUP.md`

### Getting Help
```bash
# From COMMAND mode
help

# From ASSIST mode
> How do I use this extension?

# Check status
./udos-gemini.sh --version
```

---

**🎉 Enjoy AI-powered assistance in your uDOS environment!**
