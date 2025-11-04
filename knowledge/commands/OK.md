# OK Command - AI Assistance

The `OK` command provides access to two different AI assistance systems within uDOS.

## Syntax

```bash
OK ASK <question>
OK DEV <task>
```

## Subcommands

### OK ASK - Gemini AI Assistance

Uses Google's Gemini AI for general questions, knowledge base queries, and contextual help.

**Features:**
- Natural language questions
- Local knowledge base integration
- Context-aware responses
- Works with uDOS panels and workspace

**Examples:**
```bash
OK ASK how do I implement UNDO?
OK ASK what files handle navigation?
OK ASK explain the grid system
OK ASK what is in the main panel?
```

**Requirements:**
- Gemini API key in `.env` file (optional - has offline fallback)
- Internet connection (for live AI responses)

**Fallback Mode:**
- If no API key or offline, uses local knowledge base
- Searches `/knowledge` directory for relevant content
- Returns cached documentation and examples

### OK DEV - GitHub Copilot CLI Development Tasks

Uses GitHub Copilot CLI for development-specific tasks like code generation, git help, and terminal commands.

**Features:**
- Code suggestions and generation
- Git command help
- Terminal command explanations
- Development workflow assistance

**Examples:**
```bash
OK DEV create a grid command handler
OK DEV explain this git error
OK DEV how do I fix merge conflicts
OK DEV optimize this function
```

**Requirements:**
- GitHub CLI (`gh`) installed
- GitHub Copilot CLI extension installed
- Active GitHub Copilot subscription

**Installation:**
```bash
# Install GitHub CLI
brew install gh  # macOS

# Install Copilot extension
gh extension install github/gh-copilot

# Authenticate
gh auth login
```

### OK Assisted Task Integration
- **Gemini OK Assisted Task**: Powered by Google's Gemini Pro for intelligent responses
- **Conversation History**: Maintains context across multiple questions
- **Code Analysis**: Understands programming concepts and uDOS architecture

### Response Formatting
- **Markdown Support**: Responses use proper markdown formatting
- **Code Highlighting**: Syntax highlighting for code examples
- **Structured Output**: Clear, organized responses with examples

## Related Commands

- `ANALYZE <file>` - Analyze specific files
- `EXPLAIN <topic>` - Get detailed explanations
- `GENERATE <type>` - Generate code or documentation
- `DEBUG <issue>` - Debug problems

## Configuration

### API Key Setup
The ASK command requires a Gemini API key:

1. Get API key from [Google OK Assisted Task Studio](https://makersuite.google.com/)
2. Set in environment: `export GEMINI_API_KEY=your_key_here`
3. Or add to `.env` file in project root

### Knowledge Base
- **Location**: `/knowledge` folder in uDOS root
- **Format**: Markdown files (.md)
- **Auto-indexing**: Files are automatically indexed when changed
- **Categories**: Organized by subfolder (commands, concepts, etc.)

## Examples

### Basic Questions
```bash
ASK What commands are available?
ASK How do I navigate the file system?
ASK What is the MAP command used for?
```

### Programming Help
```bash
ASK How do I write a Python function?
ASK Explain list comprehensions
ASK What are decorators in Python?
```

### uDOS Specific
```bash
ASK How do I create a custom theme?
ASK What is the grid system?
ASK How do I add a new command handler?
```

### Troubleshooting
```bash
ASK Why is my command not working?
ASK How do I fix import errors?
ASK What does this error message mean?
```

## Tips

1. **Be Specific**: More specific questions get better responses
2. **Use Context**: Reference panels or files for better context
3. **Follow Up**: Ask follow-up questions to dive deeper
4. **Check Knowledge**: Many answers are available in local knowledge base

## Technical Details

### Implementation
- **Handler**: `AssistantCommandHandler` in `core/commands/assistant_handler.py`
- **Service**: Uses `GeminiService` for OK Assisted Task integration
- **Knowledge**: `KnowledgeManager` for local search
- **Context**: Integrates with workspace and grid system

### Response Process
1. **Parse Question**: Extract question and optional panel reference
2. **Search Knowledge**: Query local knowledge base for relevant content
3. **Build Context**: Combine local knowledge with workspace information
4. **OK Assisted Task Query**: Send enhanced context to Gemini OK Assisted Task
5. **Format Response**: Process and format the OK Assisted Task response

### Error Handling
- **No API Key**: Clear instructions on setup
- **Network Issues**: Graceful fallback to local knowledge
- **Invalid Panels**: Error message for non-existent panels
- **Rate Limits**: Appropriate handling of API rate limits

## Tags
#OKAssistedTask #assist #help #questions #knowledge #documentation
