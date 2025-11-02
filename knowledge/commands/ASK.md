# ASK Command Reference

The `ASK` command provides AI-powered assistance for questions about uDOS, programming, and general topics.

## Basic Usage

```bash
ASK <question>
```

**Examples:**
```bash
ASK What is uDOS?
ASK How do I create a new file?
ASK Explain Python decorators
```

## Advanced Usage

### Ask with Panel Context
```bash
ASK <question> <panel_name>
```

The ASK command can reference content from grid panels for context-aware responses.

**Example:**
```bash
# First display code in a panel
VIEW code.py main
# Then ask about it
ASK Explain this function main
```

## Features

### Knowledge Base Integration (v1.0.8+)
- **Local Search**: ASK first searches local knowledge base for relevant content
- **Context Enhancement**: Local knowledge provides additional context for AI responses
- **Offline Capability**: Basic responses available even without internet connection

### AI Integration
- **Gemini AI**: Powered by Google's Gemini Pro for intelligent responses
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

1. Get API key from [Google AI Studio](https://makersuite.google.com/)
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
- **Service**: Uses `GeminiService` for AI integration
- **Knowledge**: `KnowledgeManager` for local search
- **Context**: Integrates with workspace and grid system

### Response Process
1. **Parse Question**: Extract question and optional panel reference
2. **Search Knowledge**: Query local knowledge base for relevant content
3. **Build Context**: Combine local knowledge with workspace information
4. **AI Query**: Send enhanced context to Gemini AI
5. **Format Response**: Process and format the AI response

### Error Handling
- **No API Key**: Clear instructions on setup
- **Network Issues**: Graceful fallback to local knowledge
- **Invalid Panels**: Error message for non-existent panels
- **Rate Limits**: Appropriate handling of API rate limits

## Tags
#AI #assistant #help #questions #knowledge #documentation
